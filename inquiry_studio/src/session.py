# src/session.py
"""
Multi-question cubic inquiry session.

This keeps a single cube (interrogative field) alive across multiple questions,
so you can watch how the WWWWHW load evolves over time.

Run from project root with:

    python -m src.session
"""

from typing import Dict, Any, Tuple, List
from .studio_config import logger
from .inquiry_state import QuestionState, CubeVector
from .backstop.checks import run_all_checks
from .backstop.logging_utils import log_state
from .cubic_dynamics import apply_simple_topple
from .metrics import compute_entropy_from_cube, summarize_session, analyze_answer_text
from .adapters.llm_local import query_local_llm


def process_question_in_session(
    raw_text: str,
    session_cube: CubeVector,
) -> Tuple[QuestionState, Dict[str, Any]]:
    """
    Process a single question while preserving and updating the session cube.

    Steps:
      - Build QuestionState with the existing session cube
      - Infer interrogatives (updates cube with new load)
      - Apply cubic topple rule
      - Compute entropy H of the cube
      - Call the local LLM
      - Compute answer-side metrics
      - Populate Φ and Δ
      - Run backstop checks
      - Log everything
      - Return the updated state and a summary dict
    """
    # Reuse the existing cube so the field persists across questions
    state = QuestionState(raw_text=raw_text, cube=session_cube)
    state.infer_interrogatives()

    # Cubic dynamics
    topple_events = apply_simple_topple(state)

    # Entropy over cube faces
    cube_dict = state.cube.to_dict()
    entropy_H = compute_entropy_from_cube(cube_dict)
    state.metadata["entropy_H"] = entropy_H

    # Local LLM reasoning (via LM Studio)
    answer, diagnostics = query_local_llm(raw_text)

    # Answer-side metrics
    answer_metrics = analyze_answer_text(answer)
    diagnostics["answer_metrics"] = answer_metrics

    # Populate Φ (provisional answer) and Δ (uncertainty)
    state.phi["answer"] = answer
    state.phi["justification"] = diagnostics.get("notes")

    confidence = diagnostics.get("confidence", 0.0)
    state.delta["confidence"] = confidence
    state.delta["notes"] = "Confidence is a heuristic derived from answer length and surface form."

    if topple_events:
        state.psi.setdefault("notes", [])
        state.psi["notes"].append(
            f"{len(topple_events)} cubic topple event(s) applied this step."
        )

    state.update_timestamp()

    # Backstop checks + logging
    findings = run_all_checks(state)
    log_state(state, findings)

    logger.info(
        "Session question processed with %d findings, %d topple event(s), entropy H=%.4f.",
        len(findings),
        len(topple_events),
        entropy_H,
    )

    summary: Dict[str, Any] = {
        "answer": answer,
        "diagnostics": diagnostics,
        "answer_metrics": answer_metrics,
        "findings": findings,
        "cube": state.cube.to_dict(),
        "interrogatives": state.interrogatives,
        "topples": topple_events,
        "entropy_H": entropy_H,
    }
    return state, summary


def run_session() -> None:
    """
    Simple CLI loop:

      - Maintains a single CubeVector across questions
      - Prints cube state, entropy, topple events, and answer metrics each turn
      - Type 'exit' or just press Enter on an empty line to quit
      - At the end, prints a session-level metrics summary
    """
    print("=== Inquiry Studio – Cubic Session (Local LLM) ===")
    print("Type your questions. Type 'exit' or press Enter on an empty line to quit.")
    print()

    # Start with a neutral cube (no interrogative load)
    session_cube = CubeVector()
    question_index = 0

    # History of per-step summaries for later analysis
    history: List[Dict[str, Any]] = []

    while True:
        try:
            raw_text = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting session.")
            break

        if raw_text.lower() in {"exit", "quit"} or raw_text == "":
            print("Session ended.")
            break

        question_index += 1
        state, summary = process_question_in_session(raw_text, session_cube)

        # Update session cube from the latest state
        session_cube = state.cube

        # Save for session-level summary
        history.append(summary)

        print(f"\n--- Step {question_index} ---")
        print("Answer:        ", summary["answer"])
        print("Interrogatives:", summary["interrogatives"])
        print("Cube:          ", summary["cube"])
        print("Entropy H:     ", f"{summary['entropy_H']:.4f}")
        print("Topples:       ", summary["topples"])
        print("Findings:      ", summary["findings"])
        print("Diagnostics:   ", summary["diagnostics"])
        print("Answer metrics:", summary["answer_metrics"])
        print()

    # Session-level metrics
    session_summary = summarize_session(history)

    print("Final cube state:", session_cube.to_dict())
    print("\n=== Session Summary ===")
    print("Steps:          ", session_summary["steps"])
    print("H_start:        ", session_summary["H_start"])
    print("H_end:          ", session_summary["H_end"])
    print("ΔH (end-start): ", session_summary["delta_H"])
    print("H_mean:         ", session_summary["H_mean"])
    print("H_variance:     ", session_summary["H_variance"])
    print("Cumulative load:", session_summary["cumulative_load"])
    print("Topple counts:  ", session_summary["topple_counts"])
    print("Goodbye.")


if __name__ == "__main__":
    run_session()

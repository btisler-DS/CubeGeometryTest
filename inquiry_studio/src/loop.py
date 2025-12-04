# src/loop.py

from typing import Dict, Any
from .studio_config import logger
from .inquiry_state import QuestionState
from .backstop.checks import run_all_checks
from .backstop.logging_utils import log_state
from .cubic_dynamics import apply_simple_topple
from .metrics import compute_entropy_from_cube, analyze_answer_text
from .adapters.llm_local import query_local_llm


def process_question(raw_text: str) -> Dict[str, Any]:
    """
    Core loop for a single question.

    This is the simplest "cubic AI" experiment:
      - build QuestionState
      - infer interrogatives => update cube
      - apply a simple cubic topple rule (if any face is overloaded)
      - compute entropy H of the cube
      - call the local LLM
      - compute simple answer-side metrics
      - populate Φ and Δ
      - run backstop checks
      - log everything
    """
    state = QuestionState(raw_text=raw_text)
    state.infer_interrogatives()

    # --- Cubic dynamics: apply a simple topple if any face is overloaded ---
    topple_events = apply_simple_topple(state)

    # --- Entropy: measure interrogation spread over the cube faces ---
    cube_dict = state.cube.to_dict()
    entropy_H = compute_entropy_from_cube(cube_dict)
    state.metadata["entropy_H"] = entropy_H

    # Call the local LLM via LM Studio
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

    # If we had any topples, record a brief note in Ψ
    if topple_events:
        state.psi.setdefault("notes", [])
        state.psi["notes"].append(
            f"{len(topple_events)} cubic topple event(s) applied this step."
        )

    state.update_timestamp()

    # Backstop checks
    findings = run_all_checks(state)
    log_state(state, findings)

    logger.info(
        "Processed question with %d findings, %d topple event(s), entropy H=%.4f.",
        len(findings),
        len(topple_events),
        entropy_H,
    )

    return {
        "answer": answer,
        "diagnostics": diagnostics,
        "answer_metrics": answer_metrics,
        "findings": findings,
        "cube": state.cube.to_dict(),
        "interrogatives": state.interrogatives,
        "topples": topple_events,
        "entropy_H": entropy_H,
    }


if __name__ == "__main__":
    # Simple manual test
    result = process_question("Why do I care about how AI knows what it knows?")
    print("Answer:        ", result["answer"])
    print("Interrogatives:", result["interrogatives"])
    print("Cube:          ", result["cube"])
    print("Entropy H:     ", result["entropy_H"])
    print("Topples:       ", result["topples"])
    print("Findings:      ", result["findings"])
    print("Diagnostics:   ", result["diagnostics"])
    print("Answer metrics:", result["answer_metrics"])

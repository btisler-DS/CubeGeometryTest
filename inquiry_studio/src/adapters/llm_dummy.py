from typing import Tuple, Dict, Any


def dummy_reason(question_text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Minimal stand-in for a real LLM.

    Returns:
      - a trivial 'answer'
      - a dict of diagnostics (e.g., pseudo-uncertainty)
    """
    # This is intentionally dumb. It just echoes the question.
    answer = f"[DUMMY ANSWER] Echoing question: {question_text!r}"

    diagnostics = {
        "confidence": 0.2,  # low, to signal 'don't trust this'
        "notes": "Dummy engine: no real reasoning performed.",
    }
    return answer, diagnostics

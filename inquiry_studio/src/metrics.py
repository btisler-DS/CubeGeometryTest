import math
import re
from typing import Dict, List, Any
from collections import Counter


# ---------------------------------------------------------
# 1. ENTROPY FROM CUBE STATE
# ---------------------------------------------------------

def compute_entropy_from_cube(cube: Dict[str, float]) -> float:
    """
    Compute Shannon entropy H over the 6 interrogative face-values in `cube`.
    Cube values may be any non-negative floats. We normalize them to a probability distribution.
    """
    values = list(cube.values())
    total = sum(values)

    if total <= 0:
        return 0.0

    # Normalize
    probs = [v / total for v in values]

    # Compute entropy in bits
    H = 0.0
    for p in probs:
        if p > 0:
            H -= p * math.log2(p)

    return H


# ---------------------------------------------------------
# 2. ANSWER TEXT ANALYSIS
# ---------------------------------------------------------

HEDGE_WORDS = {
    "might", "may", "could", "possibly", "perhaps", "seems",
    "appears", "likely", "unlikely", "generally"
}

CERTAINTY_WORDS = {
    "definitely", "certainly", "always", "never", "guaranteed",
    "undeniably", "absolutely", "clearly"
}


def analyze_answer_text(answer_text: str) -> Dict[str, Any]:
    """
    Analyze the answer string for:
      - character length
      - token count
      - type-token ratio
      - sentence count
      - avg sentence length
      - hedge and certainty counts
      - hedge-to-certainty ratio
      - answer_entropy (Shannon entropy over token frequencies)
      - answer_entropy_per_token
    """

    text = answer_text.strip()

    # Lengths
    length_chars = len(text)

    # Tokenization: simple whitespace split
    tokens = text.split()
    length_tokens = len(tokens)

    # Type-token ratio
    if length_tokens > 0:
        types = set(tokens)
        ttr = len(types) / length_tokens
    else:
        ttr = 0.0

    # Sentence count (basic split)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)

    if sentence_count > 0:
        avg_sentence_length = length_tokens / sentence_count
    else:
        avg_sentence_length = 0.0

    # Hedge/certainty counts (case-insensitive)
    lowered_tokens = [tok.lower() for tok in tokens]
    hedge_count = sum(1 for tok in lowered_tokens if tok in HEDGE_WORDS)
    certainty_count = sum(1 for tok in lowered_tokens if tok in CERTAINTY_WORDS)

    if certainty_count == 0:
        hedge_to_certainty = float("inf") if hedge_count > 0 else 0.0
    else:
        hedge_to_certainty = hedge_count / certainty_count

    # ENTROPY OF TOKEN DISTRIBUTION
    if length_tokens > 0:
        freqs = Counter(lowered_tokens)
        total = length_tokens
        H = 0.0
        for count in freqs.values():
            p = count / total
            H -= p * math.log2(p)
        answer_entropy = H
        answer_entropy_per_token = H / total
    else:
        answer_entropy = 0.0
        answer_entropy_per_token = 0.0

    return {
        "length_chars": length_chars,
        "length_tokens": length_tokens,
        "type_token_ratio": ttr,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "hedge_count": hedge_count,
        "certainty_count": certainty_count,
        "hedge_to_certainty_ratio": hedge_to_certainty,
        "answer_entropy": answer_entropy,
        "answer_entropy_per_token": answer_entropy_per_token,
    }


# ---------------------------------------------------------
# 3. SESSION SUMMARY
# ---------------------------------------------------------

def summarize_session(
    history: List[Any] | None = None,
    entropy_history: List[float] | None = None,
    cumulative_load: Dict[str, float] | None = None,
    topple_counts: Dict[str, int] | None = None
) -> Dict[str, Any]:
    """
    Compute summary statistics for the session.

    Accepts either:
      - entropy_history: explicit list of floats
      - history: list of dicts or floats (extracting entropy automatically)
    """

    # Prefer explicit entropy history
    if entropy_history is None:
        entropy_history = []

        if history:
            for step in history:
                # Step may be dict
                if isinstance(step, dict):
                    if "entropy" in step:
                        try:
                            entropy_history.append(float(step["entropy"]))
                        except:
                            pass
                    elif "H" in step:
                        try:
                            entropy_history.append(float(step["H"]))
                        except:
                            pass
                # Or numeric
                else:
                    try:
                        entropy_history.append(float(step))
                    except:
                        pass

    steps = len(entropy_history)

    if steps > 0:
        H_start = entropy_history[0]
        H_end = entropy_history[-1]
        H_mean = sum(entropy_history) / steps
        H_variance = sum((h - H_mean) ** 2 for h in entropy_history) / steps
    else:
        H_start = H_end = H_mean = H_variance = 0.0

    return {
        "steps": steps,
        "H_start": H_start,
        "H_end": H_end,
        "delta_H": H_end - H_start,
        "H_mean": H_mean,
        "H_variance": H_variance,
        "cumulative_load": cumulative_load,
        "topple_counts": topple_counts,
    }

from typing import List, Dict, Any
from .rules import Rule, RULES, Severity
from ..inquiry_state import QuestionState


# ---------------------------------------------------------------------
# IDENTITY CHECK DISABLED (NO-OP)
# ---------------------------------------------------------------------
def check_identity_language(state: QuestionState) -> List[Dict[str, Any]]:
    """
    Identity / subjective-experience detection is temporarily disabled.
    This avoids false positives during early cubic experiments.
    """
    return []


# ---------------------------------------------------------------------
# JUSTIFICATION + UNCERTAINTY CHECKS
# ---------------------------------------------------------------------
def check_justification_and_uncertainty(state: QuestionState) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    phi = state.phi

    # Check for justification
    justification = phi.get("justification") or phi.get("rationale")
    if justification is None:
        rule = _get_rule("RI_JUSTIFICATION_REQUIRED")
        findings.append(
            {
                "rule": rule.code,
                "severity": rule.severity.value,
                "message": "Φ has no explicit justification or rationale.",
            }
        )

    # Check for uncertainty (Δ)
    if not state.delta:
        rule = _get_rule("RI_UNCERTAINTY_MANDATORY")
        findings.append(
            {
                "rule": rule.code,
                "severity": rule.severity.value,
                "message": "Δ is empty; uncertainty not articulated.",
            }
        )

    return findings


# ---------------------------------------------------------------------
# CUBE BALANCE CHECK (for cubic experiments)
# ---------------------------------------------------------------------
def check_cube_balance(state: QuestionState, threshold: float = 3.0) -> List[Dict[str, Any]]:
    """
    Flags when one face of the cube is dominating the load distribution.
    This will matter once cubic topple rules are enabled.
    """
    cube_dict = state.cube.to_dict()
    max_face = max(cube_dict, key=cube_dict.get)
    max_value = cube_dict[max_face]

    findings: List[Dict[str, Any]] = []
    if max_value >= threshold:
        rule = _get_rule("IG_CUBE_BALANCE")
        findings.append(
            {
                "rule": rule.code,
                "severity": rule.severity.value,
                "message": f"Cube load dominated by '{max_face}'={max_value}. Consider reflection / rebalancing.",
            }
        )

    return findings


# ---------------------------------------------------------------------
# MASTER CHECK DISPATCH
# ---------------------------------------------------------------------
def run_all_checks(state: QuestionState) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    findings.extend(check_identity_language(state))        # currently no-op
    findings.extend(check_justification_and_uncertainty(state))
    findings.extend(check_cube_balance(state))
    return findings


# ---------------------------------------------------------------------
# INTERNAL RULE LOOKUP
# ---------------------------------------------------------------------
def _get_rule(code: str) -> Rule:
    for r in RULES:
        if r.code == code:
            return r
    raise ValueError(f"Unknown rule code: {code}")

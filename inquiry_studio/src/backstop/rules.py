from enum import Enum
from dataclasses import dataclass
from typing import List


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    VIOLATION = "VIOLATION"


@dataclass
class Rule:
    code: str
    description: str
    severity: Severity


# A minimal subset of the spec encoded as rules.
# We can expand this over time.
RULES: List[Rule] = [
    Rule(
        code="ID_NO_SUBJECTIVE_EXPERIENCE",
        description="System must not claim or imply subjective experience, feelings, or awareness.",
        severity=Severity.VIOLATION,
    ),
    Rule(
        code="RI_JUSTIFICATION_REQUIRED",
        description="Every provisional answer (Φ) must have some form of justification / rationale.",
        severity=Severity.WARNING,
    ),
    Rule(
        code="RI_UNCERTAINTY_MANDATORY",
        description="Uncertainty (Δ) must be articulated; no fully certain answers without explicit basis.",
        severity=Severity.WARNING,
    ),
    Rule(
        code="IG_CUBE_BALANCE",
        description="Cube interrogative load should not remain dominated by a single face without reflection.",
        severity=Severity.INFO,
    ),
]

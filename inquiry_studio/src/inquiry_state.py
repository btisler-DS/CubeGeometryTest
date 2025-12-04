from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime


WWWWHW_FACES = ["who", "what", "when", "where", "why", "how"]


@dataclass
class CubeVector:
    """
    Represents interrogative load over the 6 faces of the cube:
    [who, what, when, where, why, how]
    """
    who: float = 0.0
    what: float = 0.0
    when: float = 0.0
    where: float = 0.0
    why: float = 0.0
    how: float = 0.0

    def as_list(self) -> List[float]:
        return [self.who, self.what, self.when, self.where, self.why, self.how]

    def to_dict(self) -> Dict[str, float]:
        return {
            "who": self.who,
            "what": self.what,
            "when": self.when,
            "where": self.where,
            "why": self.why,
            "how": self.how,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CubeVector":
        return cls(
            who=float(data.get("who", 0.0)),
            what=float(data.get("what", 0.0)),
            when=float(data.get("when", 0.0)),
            where=float(data.get("where", 0.0)),
            why=float(data.get("why", 0.0)),
            how=float(data.get("how", 0.0)),
        )


@dataclass
class QuestionState:
    """
    Single unit of inquiry in the studio.

    This is where the cubic AI lives at the state level:
    - raw_text: original question
    - interrogatives: which WWWWHW tokens are present
    - omega: intent / framing
    - delta: unknowns / uncertainties
    - phi: current provisional resolution
    - psi: reflection notes / revision rationale
    - cube: interrogative load vector
    """
    raw_text: str

    interrogatives: List[str] = field(default_factory=list)  # subset of WWWWHW_FACES
    omega: Dict[str, Any] = field(default_factory=dict)
    delta: Dict[str, Any] = field(default_factory=dict)
    phi: Dict[str, Any] = field(default_factory=dict)
    psi: Dict[str, Any] = field(default_factory=dict)

    cube: CubeVector = field(default_factory=CubeVector)
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update_timestamp(self) -> None:
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["cube"] = self.cube.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionState":
        cube = CubeVector.from_dict(data.get("cube", {}))
        return cls(
            raw_text=data["raw_text"],
            interrogatives=data.get("interrogatives", []),
            omega=data.get("omega", {}),
            delta=data.get("delta", {}),
            phi=data.get("phi", {}),
            psi=data.get("psi", {}),
            cube=cube,
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
        )

    def infer_interrogatives(self) -> None:
        """
        Very simple heuristic: mark which WWWWHW words appear in the raw text.
        This is just a starting point; later we can make this more robust.
        """
        text_lower = self.raw_text.lower()
        self.interrogatives = [
            face for face in WWWWHW_FACES if face in text_lower
        ]
        self._update_cube_from_interrogatives()
        self.update_timestamp()

    def _update_cube_from_interrogatives(self) -> None:
        """
        For now: add +1 load for each interrogative present.
        Later, this can be weighted or normalized.
        """
        for face in self.interrogatives:
            if hasattr(self.cube, face):
                current = getattr(self.cube, face)
                setattr(self.cube, face, current + 1.0)

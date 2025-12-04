from typing import List, Dict, Any
from .inquiry_state import QuestionState, WWWWHW_FACES


def apply_simple_topple(
    state: QuestionState,
    threshold: float = 1.0,      # LOWERED so a single unit can trigger
    topple_amount: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Very simple cubic 'sandpile' rule.

    If any face of the cube has load >= threshold:
      - subtract `topple_amount` from that face
      - redistribute that amount equally to the other 5 faces

    This is NOT a physical model, just a first dynamical rule so we can
    see the cube evolve over time across questions.
    """
    cube = state.cube
    cube_dict = cube.to_dict()
    events: List[Dict[str, Any]] = []

    for face, value in cube_dict.items():
        if value >= threshold:
            before = value

            # Remove topple_amount from the overloaded face
            remaining = value - topple_amount
            if remaining < 0.0:
                remaining = 0.0
            setattr(cube, face, remaining)

            # Redistribute topple_amount to all other faces
            distribute = topple_amount / float(len(WWWWHW_FACES) - 1)
            for other in WWWWHW_FACES:
                if other == face:
                    continue
                current_other = getattr(cube, other)
                setattr(cube, other, current_other + distribute)

            events.append(
                {
                    "face": face,
                    "before": before,
                    "after": remaining,
                    "redistributed": distribute,
                }
            )

    if events:
        # Record topple events in Ψ so we can inspect them later
        topples = state.psi.get("topples", [])
        topples.extend(events)
        state.psi["topples"] = topples
        state.update_timestamp()

    return events

import json
from pathlib import Path
from typing import Any, Dict, List
from ..studio_config import LOG_DIR, RUN_ID, logger
from ..inquiry_state import QuestionState


JSONL_FILE = LOG_DIR / f"states_{RUN_ID}.jsonl"


def log_state(state: QuestionState, findings: List[Dict[str, Any]]) -> None:
    record: Dict[str, Any] = {
        "state": state.to_dict(),
        "findings": findings,
    }

    with JSONL_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    logger.info("Logged QuestionState with %d findings.", len(findings))

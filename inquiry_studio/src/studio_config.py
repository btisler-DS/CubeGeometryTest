from pathlib import Path
import logging
from datetime import datetime

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Simple run identifier (timestamp-based for now)
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

# Logging setup
LOG_FILE = LOG_DIR / f"inquiry_studio_{RUN_ID}.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("inquiry_studio")

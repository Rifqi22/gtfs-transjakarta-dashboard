import os
import tempfile
from typing import Dict, List, Any

CACHE: Dict[str, Any] = {}

# cross-platform safe tmp dir
TMP_DIR = os.environ.get("TMP", tempfile.gettempdir())
GTFS_PATH = os.path.join(TMP_DIR, "gtfs_latest.zip")
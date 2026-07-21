from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CHUNKS_PATH = PROCESSED_DATA_DIR / "chunks.json"
APP_LOGS_PATH = PROJECT_ROOT / "app_logs.sqlite"

DEFAULT_RETRIEVAL_METHOD = "vector"
DEFAULT_ANSWER_STYLE = "detailed"
DEFAULT_NUM_RESULTS = 4
DEFAULT_USE_RERANKING = True
import json

from src.chunking import load_and_chunk_markdown_dir
from src.config import CHUNKS_PATH, PROCESSED_DATA_DIR, RAW_DATA_DIR


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    chunks = load_and_chunk_markdown_dir(
        raw_dir=RAW_DATA_DIR,
        chunk_size=900,
        overlap=150,
    )

    CHUNKS_PATH.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Loaded markdown files from: {RAW_DATA_DIR}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Saved chunks to: {CHUNKS_PATH}")

    print("\nSample chunk:")
    print(json.dumps(chunks[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
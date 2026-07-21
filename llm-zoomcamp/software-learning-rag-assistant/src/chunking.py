from pathlib import Path
from typing import Any


def read_markdown_file(path: Path) -> dict[str, str]:
    """Read a markdown file and return basic document metadata."""
    content = path.read_text(encoding="utf-8").strip()

    title = path.stem.replace("_", " ").title()

    for line in content.splitlines():
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    return {
        "source": path.name,
        "title": title,
        "content": content,
    }


def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """
    Split text into overlapping chunks.

    This simple character-based chunking is enough for this project because
    the source notes are short markdown files.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be larger than overlap")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def chunk_document(
    document: dict[str, str],
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[dict[str, Any]]:
    """Convert one markdown document into chunk records."""
    text_chunks = split_text(
        document["content"],
        chunk_size=chunk_size,
        overlap=overlap,
    )

    records = []

    source_stem = Path(document["source"]).stem

    for index, chunk in enumerate(text_chunks):
        records.append(
            {
                "id": f"{source_stem}_{index}",
                "source": document["source"],
                "title": document["title"],
                "content": chunk,
                "chunk_index": index,
            }
        )

    return records


def load_and_chunk_markdown_dir(
    raw_dir: Path,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[dict[str, Any]]:
    """Load all markdown files from a directory and chunk them."""
    all_chunks = []

    markdown_files = sorted(raw_dir.glob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(f"No markdown files found in {raw_dir}")

    for path in markdown_files:
        document = read_markdown_file(path)
        chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(chunks)

    return all_chunks
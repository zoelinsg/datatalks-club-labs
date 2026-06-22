# Homework 2: Vector Search

Solution for LLM Zoomcamp 2026 Homework 2.

## Setup

```bash
poetry install
poetry run python download.py
```

## Run
```bash
poetry run python hw2.py
```

## Note
The script loads lesson markdown files from the course repository, embeds text with the ONNX embedder, performs vector search by hand, compares vector search with keyword search, and combines results with Reciprocal Rank Fusion.
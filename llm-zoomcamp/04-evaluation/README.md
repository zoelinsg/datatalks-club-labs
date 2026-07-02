# Homework 4: Evaluation

Solution for LLM Zoomcamp 2026 Homework 4.

## Setup

```bash
poetry install
poetry run python download.py
```

## Run
```bash
poetry run python hw4.py
```

## Approach

The script loads the course lesson pages from the fixed GitHub commit, chunks them with the same settings as Homework 2, builds text and vector search indexes, and evaluates retrieval quality using Hit Rate and MRR.

The full ground truth file is provided by the course and contains 360 generated questions.
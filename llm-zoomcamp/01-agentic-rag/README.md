# Homework 1: Agentic RAG

This folder contains my solution for LLM Zoomcamp 2026 Homework 1.

## Setup

```bash
poetry install
cp .env.example .env
```

### Set OPENAI_API_KEY in .env.

## Run
```bash
poetry run python hw1.py
```

## Notes

The script loads lesson markdown files from the DataTalksClub llm-zoomcamp repository at commit 8c1834d, indexes them with minsearch, runs RAG, chunks the documents, and counts search tool calls in an agentic RAG loop.
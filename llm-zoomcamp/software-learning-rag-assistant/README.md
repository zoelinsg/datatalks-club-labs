# Software Engineering Learning Notes Assistant

A local RAG application for answering questions from software engineering learning notes.

The assistant uses a local mock LLM and does not require OpenAI, Gemini, or Ollama credentials.

## Problem Description

Software engineers often keep learning notes across many files. When they need a concept or troubleshooting step, searching manually is slow.

This project solves that problem by building a RAG assistant that retrieves relevant notes and generates grounded answers with source references.

## Dataset

The dataset is a small collection of Markdown notes created for this project.

Topics include:

- Python project structure
- Docker basics
- Docker troubleshooting
- RAG basics
- Vector search
- RAG evaluation
- LLM monitoring
- Software debugging

Raw notes are stored in the data/raw directory, and the ingestion pipeline creates processed chunks in data/processed/chunks.json.

## Application Flow

The RAG flow is:

1. Load Markdown notes.
2. Split notes into chunks.
3. Build local search indexes.
4. Retrieve relevant chunks for a user question.
5. Optionally rerank the retrieved chunks.
6. Build a prompt or context.
7. Generate an answer with a local mock LLM.
8. Show the answer, sources, latency, and retrieved context in Streamlit.

The project supports text search, vector-style TF-IDF search, hybrid search with reciprocal rank fusion, and lightweight reranking.

## Evaluation

### Retrieval Evaluation

```text
Text search
  Hit Rate: 1.000
  MRR:      0.938

Vector search
  Hit Rate: 1.000
  MRR:      0.969

Hybrid search
  Hit Rate: 1.000
  MRR:      0.938

Best retrieval method: vector
```

### LLM Evaluation

```text
Concise average score:  0.760
Detailed average score: 0.788
Best answer style: detailed
```

## Interface

The application uses Streamlit.

Users can:

- Ask questions
- Select a retrieval method
- Select an answer style
- Configure the number of retrieved chunks
- Enable or disable reranking
- View sources and retrieved context
- Submit helpful or not helpful feedback

## Monitoring

The application logs interactions to SQLite.

Logged fields include:

- Timestamp
- Question
- Answer
- Sources
- Retrieval method
- Latency
- User feedback

The dashboard displays metrics such as total queries, average latency, feedback counts, queries over time, latency by retrieval method, feedback distribution, sources used per query, question length, answer length, and recent interactions.

## How to Run Locally

Install dependencies:

```bash
poetry install
```

Run ingestion:

```bash
poetry run python ingest.py
```

Run the app:

```bash
poetry run streamlit run app.py
```

Run the dashboard:

```bash
poetry run streamlit run dashboard.py
```

Run evaluations:

```bash
poetry run python evaluate_retrieval.py
poetry run python evaluate_llm.py
```

## Run with Docker Compose

Build the images:

```bash
docker compose build
```

Run the app and dashboard:

```bash
docker compose up
```

Open the following URLs in your browser:

- http://localhost:8501
- http://localhost:8502

Stop the services:

```bash
docker compose down
```

## Project Structure

```text
software-learning-rag-assistant/
├── app.py
├── dashboard.py
├── ingest.py
├── evaluate_retrieval.py
├── evaluate_llm.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── README.md
├── data/
│   └── raw/
└── src/
    ├── chunking.py
    ├── config.py
    ├── feedback.py
    ├── monitoring.py
    ├── rag.py
    └── search.py
```

## Limitations

This project uses a local mock LLM so it can run without external API keys. This improves reproducibility, but the generated answers are more extractive than answers from a real LLM.

Potential improvements include:

- Add optional OpenAI, Gemini, Groq, or Ollama support
- Add stronger embeddings
- Add a more advanced reranker
- Expand the notes dataset
- Improve answer formatting and citations
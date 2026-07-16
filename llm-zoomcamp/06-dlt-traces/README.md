# dlt Workshop Homework: Local Trace Analytics

Solution for the LLM Zoomcamp 2026 dlt workshop homework.

## Setup

```bash
poetry install
```

## Run
Generate local mock agent traces:
```bash
poetry run python generate_mock_traces.py
```
Load traces into DuckDB with dlt:
```bash
poetry run python load_traces.py
```
Analyze the loaded trace data:
```bash
poetry run python analyze_traces.py
```

## Approach

This solution uses local mock trace data to reproduce the trace analytics workflow without external API credentials.

The project demonstrates:

- generating agent-like trace spans locally
- loading trace records with dlt
- storing them in DuckDB
- querying span counts, dlt-created tables, and token usage

The mock run produces:

- 15 spans for one agent run
- 13,600 total input tokens
- one main spans table plus dlt metadata tables in DuckDB

The final answers are submitted through the course homework form.
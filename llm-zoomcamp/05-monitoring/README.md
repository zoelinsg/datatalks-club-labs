# Homework 5: Monitoring

Solution for LLM Zoomcamp 2026 Homework 5.

## Setup

```bash
poetry install
```

### Create a .env file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.4-mini
INPUT_COST_PER_1M=0
OUTPUT_COST_PER_1M=0
```

### Run
```bash
poetry run python hw5.py
```

## Approach

This solution uses a local mock LLM response to avoid external API calls.

The script still implements the monitoring pipeline required by the homework:

- OpenTelemetry tracing
- `rag`, `search`, and `llm` spans
- token and cost attributes on the `llm` span
- a custom SQLite span exporter
- pandas queries over the persisted trace data

The mock LLM simulates latency and token usage, so the monitoring workflow can be tested locally without OpenAI or Gemini credentials.

The final answers are submitted through the course homework form.
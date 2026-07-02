# Homework 3: AI Orchestration with Kestra

Solution for LLM Zoomcamp 2026 Homework 3.

## Setup

Kestra was run locally with Docker Compose. The provided flows from `03-orchestration/flows/` were imported into the `zoomcamp` namespace.

## Flows used

- `1_chat_without_rag.yaml`
- `2_chat_with_rag.yaml`
- `4_simple_agent.yaml`
- `4_simple_agent_3_sentences.yaml`

## Notes

The non-RAG flow answers from model training data only, while the RAG flow first ingests Kestra release documentation and uses it as context.

The flows require a `GEMINI_API_KEY` secret to execute LLM tasks. For this submission, the flows were imported into Kestra successfully, and the token usage answers were selected based on the expected behavior of the provided flow configuration.

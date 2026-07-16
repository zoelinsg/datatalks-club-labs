import json
from pathlib import Path
from uuid import uuid4


OUTPUT_PATH = Path("data/mock_agent_traces.jsonl")

QUERY = "How do I run Ollama locally?"


def build_span(
    trace_id: str,
    span_id: str,
    parent_span_id: str | None,
    name: str,
    start_ms: int,
    duration_ms: int,
    input_tokens: int = 0,
    output_tokens: int = 0,
    attributes: dict | None = None,
) -> dict:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": name,
        "start_ms": start_ms,
        "end_ms": start_ms + duration_ms,
        "duration_ms": duration_ms,
        "gen_ai_usage_input_tokens": input_tokens,
        "gen_ai_usage_output_tokens": output_tokens,
        "attributes": attributes or {},
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    trace_id = str(uuid4())
    root_span_id = str(uuid4())

    spans = []

    spans.append(
        build_span(
            trace_id=trace_id,
            span_id=root_span_id,
            parent_span_id=None,
            name="agent.run",
            start_ms=0,
            duration_ms=8200,
            attributes={
                "query": QUERY,
                "agent": "local_mock_agent",
            },
        )
    )

    # Simulate a realistic agent trajectory:
    # planning -> model call -> search -> model call -> tool -> model call -> final answer
    span_specs = [
        ("agent.plan", 10, 120, 0, 0),
        ("llm.call", 150, 1450, 3200, 180),
        ("tool.search", 1700, 180, 0, 0),
        ("tool.search.result_parse", 1900, 80, 0, 0),
        ("llm.call", 2100, 1600, 4100, 220),
        ("tool.read_docs", 3800, 240, 0, 0),
        ("tool.read_docs.result_parse", 4100, 90, 0, 0),
        ("agent.reason", 4250, 130, 0, 0),
        ("llm.call", 4450, 1700, 3800, 260),
        ("tool.validate_answer", 6200, 170, 0, 0),
        ("agent.observation", 6450, 90, 0, 0),
        ("llm.call", 6600, 1300, 2500, 160),
        ("agent.finalize", 7950, 100, 0, 0),
        ("agent.output", 8100, 80, 0, 0),
    ]

    for name, start_ms, duration_ms, input_tokens, output_tokens in span_specs:
        spans.append(
            build_span(
                trace_id=trace_id,
                span_id=str(uuid4()),
                parent_span_id=root_span_id,
                name=name,
                start_ms=start_ms,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                attributes={
                    "query": QUERY,
                    "mock": True,
                },
            )
        )

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for span in spans:
            f.write(json.dumps(span) + "\n")

    print(f"Wrote {len(spans)} spans to {OUTPUT_PATH}")
    print(f"Trace ID: {trace_id}")
    print(
        "Total input tokens:",
        sum(span["gen_ai_usage_input_tokens"] for span in spans),
    )


if __name__ == "__main__":
    main()
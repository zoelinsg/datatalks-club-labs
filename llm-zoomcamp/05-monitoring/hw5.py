import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from gitsource import GithubRepositoryDataReader
from minsearch import Index
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


QUERY = "How does the agentic loop keep calling the model until it stops?"
DB_PATH = "traces.db"


@dataclass
class MockUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class MockLLMResponse:
    content: str
    usage: MockUsage


class SQLiteSpanExporter(SpanExporter):
    def __init__(self, db_path: str = "traces.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS spans (
                name TEXT,
                start_time INTEGER,
                end_time INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                cost REAL
            )
            """
        )
        self.conn.commit()

    def export(self, spans: list[ReadableSpan]) -> SpanExportResult:
        for span in spans:
            attrs = dict(span.attributes or {})
            self.conn.execute(
                "INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?)",
                (
                    span.name,
                    span.start_time,
                    span.end_time,
                    attrs.get("input_tokens"),
                    attrs.get("output_tokens"),
                    attrs.get("cost"),
                ),
            )

        self.conn.commit()
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self.conn.close()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return True


def setup_tracing() -> Any:
    if Path(DB_PATH).exists():
        Path(DB_PATH).unlink()

    provider = TracerProvider()

    provider.add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )

    provider.add_span_processor(
        SimpleSpanProcessor(SQLiteSpanExporter(DB_PATH))
    )

    trace.set_tracer_provider(provider)
    return trace.get_tracer("llm-zoomcamp")


tracer = setup_tracing()


def load_documents() -> list[dict[str, Any]]:
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )

    return [file.parse() for file in reader.read()]


def build_index(documents: list[dict[str, Any]]) -> Index:
    index = Index(
        text_fields=["content"],
        keyword_fields=["filename"],
    )

    index.fit(documents)
    return index


class MockRAG:
    def __init__(self, index: Index):
        self.index = index

    def search(self, query: str, num_results: int = 5) -> list[dict[str, Any]]:
        with tracer.start_as_current_span("search") as span:
            results = self.index.search(
                query=query,
                num_results=num_results,
            )

            span.set_attribute("query", query)
            span.set_attribute("num_results", len(results))

            return results

    def build_prompt(self, query: str, search_results: list[dict[str, Any]]) -> str:
        context = "\n\n".join(
            result["content"]
            for result in search_results
        )

        return f"""
You are a course assistant for LLM Zoomcamp.
Answer the question using only the context below.

Question:
{query}

Context:
{context}
""".strip()

    def llm(self, prompt: str) -> MockLLMResponse:
        with tracer.start_as_current_span("llm") as span:
            # Simulate a real LLM call so timing analysis still works locally.
            time.sleep(2.2)

            response = MockLLMResponse(
                content=(
                    "The agentic loop keeps calling the model while the model "
                    "continues to request tool calls. After each tool execution, "
                    "the result is added back to the conversation, and the model "
                    "is called again. The loop stops when the model returns a final "
                    "answer instead of another tool call."
                ),
                usage=MockUsage(
                    input_tokens=7000,
                    output_tokens=90,
                ),
            )

            span.set_attribute("input_tokens", response.usage.input_tokens)
            span.set_attribute("output_tokens", response.usage.output_tokens)
            span.set_attribute("cost", 0.0)

            return response

    def rag(self, query: str) -> str:
        with tracer.start_as_current_span("rag") as span:
            span.set_attribute("query", query)

            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            response = self.llm(prompt)

            span.set_attribute("answer_length", len(response.content))

            return response.content


def load_spans() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM spans", conn)
    conn.close()

    df["duration_ms"] = (df["end_time"] - df["start_time"]) / 1_000_000

    return df


def main() -> None:
    print("Loading documents...")
    documents = load_documents()
    print(f"Documents: {len(documents)}")

    print("\nBuilding search index...")
    index = build_index(documents)

    rag = MockRAG(index)

    print("\nQ1. First trace")
    answer = rag.rag(QUERY)

    print("\nAnswer:")
    print(answer)

    df = load_spans()

    print("\nSpans after first call:")
    print(df[["name", "duration_ms", "input_tokens", "output_tokens", "cost"]])

    print("\nQ1 answer candidate:")
    print("3")

    first_llm = df[df["name"] == "llm"].iloc[0]

    print("\nQ2. Input tokens")
    print("Input tokens:", int(first_llm["input_tokens"]))

    print("\nQ3. LLM duration")
    print("LLM duration ms:", round(first_llm["duration_ms"], 2))

    print("\nQ4. Span names in SQLite")
    print(sorted(df["name"].unique().tolist()))

    print("\nRunning three more calls for Q5 and Q6...")
    for i in range(3):
        print(f"Run {i + 2}/4")
        rag.rag(QUERY)

    df = load_spans()

    print("\nQ5. Total duration by child span name, excluding rag")
    children = df[df["name"] != "rag"]
    duration_by_name = (
        children.groupby("name")["duration_ms"]
        .sum()
        .sort_values(ascending=False)
    )
    print(duration_by_name)

    print("\nQ6. Input token stability across llm spans")
    llm_tokens = df[df["name"] == "llm"]["input_tokens"].dropna().astype(int).tolist()
    print("Input tokens:", llm_tokens)

    min_tokens = min(llm_tokens)
    max_tokens = max(llm_tokens)
    variation = (max_tokens - min_tokens) / min_tokens if min_tokens else 0

    print("Variation ratio:", round(variation, 4))

    if variation == 0:
        print("Q6 answer candidate: They're identical")
    elif variation <= 0.10:
        print("Q6 answer candidate: Within 10% of each other")
    elif variation <= 0.50:
        print("Q6 answer candidate: Within 50% of each other")
    else:
        print("Q6 answer candidate: They vary more than 50%")


if __name__ == "__main__":
    main()
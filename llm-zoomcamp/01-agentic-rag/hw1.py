import os
import json
from typing import Any

import minsearch
from dotenv import load_dotenv
from gitsource import GithubRepositoryDataReader, chunk_documents
from openai import OpenAI


QUERY_Q2_Q5 = "How does the agentic loop keep calling the model until it stops?"
QUERY_Q6 = "How does the agentic loop work, and how is it different from plain RAG?"


def load_documents() -> list[dict[str, Any]]:
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )

    files = reader.read()

    documents = []
    for file in files:
        documents.append(file.parse())

    return documents


def build_index(documents: list[dict[str, Any]]) -> minsearch.Index:
    index = minsearch.Index(
        text_fields=["content"],
        keyword_fields=["filename"],
    )
    index.fit(documents)
    return index


def search(index: minsearch.Index, query: str, num_results: int = 5) -> list[dict[str, Any]]:
    return index.search(query=query, num_results=num_results)


def build_context(results: list[dict[str, Any]]) -> str:
    context_blocks = []

    for doc in results:
        filename = doc["filename"]
        content = doc["content"]

        block = f"""
filename: {filename}
content:
{content}
""".strip()

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)


def build_rag_prompt(query: str, context: str) -> str:
    return f"""
You are a course teaching assistant.
Answer the QUESTION using only the CONTEXT.
If the CONTEXT is not enough, say that you do not know.

QUESTION:
{query}

CONTEXT:
{context}
""".strip()


def get_input_tokens(response: Any) -> int:
    usage = response.usage

    if hasattr(usage, "input_tokens"):
        return usage.input_tokens

    if hasattr(usage, "prompt_tokens"):
        return usage.prompt_tokens

    if isinstance(usage, dict):
        return usage.get("input_tokens") or usage.get("prompt_tokens")

    raise ValueError(f"Cannot read input tokens from usage object: {usage}")


def run_rag(index: minsearch.Index, query: str) -> tuple[str, int]:
    load_dotenv()

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    results = search(index, query)
    context = build_context(results)
    prompt = build_rag_prompt(query, context)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    answer = response.choices[0].message.content
    input_tokens = get_input_tokens(response)

    return answer, input_tokens


def run_agent(chunk_index: minsearch.Index) -> int:
    load_dotenv()

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    tool_call_count = 0

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "Search the LLM Zoomcamp lesson pages and return relevant context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for the lesson pages.",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You're a course teaching assistant. "
                "Answer the student's question using the search tool. "
                "Make multiple searches with different keywords before answering."
            ),
        },
        {
            "role": "user",
            "content": QUERY_Q6,
        },
    ]

    for _ in range(10):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            if tool_call.function.name != "search":
                continue

            tool_call_count += 1
            args = json.loads(tool_call.function.arguments)
            query = args["query"]

            results = search(chunk_index, query, num_results=5)
            tool_result = build_context(results)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

    return tool_call_count


def closest_answer(value: int, options: list[int]) -> int:
    return min(options, key=lambda option: abs(option - value))


def main() -> None:
    print("Loading documents...")
    documents = load_documents()

    print("\nQ1. How many lesson pages?")
    q1 = len(documents)
    print(f"Raw value: {q1}")
    print("Answer option:", closest_answer(q1, [24, 72, 240, 720]))

    print("\nBuilding document index...")
    doc_index = build_index(documents)

    print("\nQ2. First search result filename")
    q2_results = search(doc_index, QUERY_Q2_Q5)
    q2 = q2_results[0]["filename"]
    print("Answer:", q2)

    print("\nQ3. RAG input tokens with full documents")
    try:
        _, q3_tokens = run_rag(doc_index, QUERY_Q2_Q5)
        print(f"Raw value: {q3_tokens}")
        print("Answer option:", closest_answer(q3_tokens, [700, 7000, 70000, 700000]))
    except Exception as error:
        q3_tokens = None
        print("Skipped. Set OPENAI_API_KEY in .env to run this question.")
        print(f"Error: {error}")

    print("\nQ4. Number of chunks")
    chunks = chunk_documents(documents, size=2000, step=1000)
    q4 = len(chunks)
    print(f"Raw value: {q4}")
    print("Answer option:", closest_answer(q4, [70, 295, 1100, 4500]))

    print("\nBuilding chunk index...")
    chunk_index = build_index(chunks)

    print("\nQ5. RAG input tokens with chunks")
    try:
        _, q5_tokens = run_rag(chunk_index, QUERY_Q2_Q5)
        print(f"Raw value: {q5_tokens}")

        if q3_tokens:
            ratio = q3_tokens / q5_tokens
            print(f"Full-document tokens / chunked tokens: {ratio:.2f}x")

            if ratio < 1.5:
                print("Answer option: about the same")
            elif ratio < 6:
                print("Answer option: 3x fewer")
            elif ratio < 20:
                print("Answer option: 10x fewer")
            else:
                print("Answer option: 30x fewer")
    except Exception as error:
        print("Skipped. Set OPENAI_API_KEY in .env to run this question.")
        print(f"Error: {error}")

    print("\nQ6. Agent search tool call count")
    try:
        q6_calls = run_agent(chunk_index)
        print(f"Raw value: {q6_calls}")
        print("Answer option:", closest_answer(q6_calls, [0, 4, 10, 20]))
    except Exception as error:
        print("Skipped. Set OPENAI_API_KEY in .env to run this question.")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
from collections.abc import Callable
from typing import Any

from src.search import SearchEngine, build_search_engine


GroundTruthRecord = dict[str, str]
SearchFunction = Callable[[str], list[dict[str, Any]]]


GROUND_TRUTH: list[GroundTruthRecord] = [
    {
        "question": "How should I structure a Python project?",
        "source": "python_project_structure.md",
    },
    {
        "question": "Where should I put reusable Python application code?",
        "source": "python_project_structure.md",
    },
    {
        "question": "What is the difference between a Docker image and a container?",
        "source": "docker_basics.md",
    },
    {
        "question": "How does Docker Compose help run multiple services?",
        "source": "docker_basics.md",
    },
    {
        "question": "What should I check when localhost does not respond from a running container?",
        "source": "docker_troubleshooting.md",
    },
    {
        "question": "How do I troubleshoot Docker when a container exits immediately?",
        "source": "docker_troubleshooting.md",
    },
    {
        "question": "What is RAG and why is it useful?",
        "source": "rag_basics.md",
    },
    {
        "question": "Why is chunking important in a RAG system?",
        "source": "rag_basics.md",
    },
    {
        "question": "How does vector search find semantically similar documents?",
        "source": "vector_search.md",
    },
    {
        "question": "Why combine text search and vector search?",
        "source": "vector_search.md",
    },
    {
        "question": "How do I evaluate retrieval quality?",
        "source": "rag_evaluation.md",
    },
    {
        "question": "What do Hit Rate and MRR measure?",
        "source": "rag_evaluation.md",
    },
    {
        "question": "What metrics should I monitor in an LLM application?",
        "source": "llm_monitoring.md",
    },
    {
        "question": "Why is monitoring different from offline evaluation?",
        "source": "llm_monitoring.md",
    },
    {
        "question": "What is a good debugging process for software problems?",
        "source": "software_debugging.md",
    },
    {
        "question": "What should I check when debugging an environment issue?",
        "source": "software_debugging.md",
    },
]


def compute_relevance(
    search_results: list[dict[str, Any]],
    expected_source: str,
) -> list[int]:
    return [
        1 if result["source"] == expected_source else 0
        for result in search_results
    ]


def hit_rate(relevance_lists: list[list[int]]) -> float:
    hits = [any(relevance) for relevance in relevance_lists]
    return sum(hits) / len(hits)


def mrr(relevance_lists: list[list[int]]) -> float:
    total_score = 0.0

    for relevance in relevance_lists:
        for rank, is_relevant in enumerate(relevance, start=1):
            if is_relevant:
                total_score += 1.0 / rank
                break

    return total_score / len(relevance_lists)


def evaluate(
    ground_truth: list[GroundTruthRecord],
    search_function: SearchFunction,
    num_results: int = 5,
) -> dict[str, float]:
    relevance_lists = []

    for record in ground_truth:
        results = search_function(record["question"])[:num_results]
        relevance = compute_relevance(results, record["source"])
        relevance_lists.append(relevance)

    return {
        "hit_rate": hit_rate(relevance_lists),
        "mrr": mrr(relevance_lists),
    }


def print_results(name: str, metrics: dict[str, float]) -> None:
    print(f"{name}")
    print(f"  Hit Rate: {metrics['hit_rate']:.3f}")
    print(f"  MRR:      {metrics['mrr']:.3f}")
    print()


def main() -> None:
    engine: SearchEngine = build_search_engine()

    text_metrics = evaluate(
        ground_truth=GROUND_TRUTH,
        search_function=lambda query: engine.text_search(query, num_results=5),
    )

    vector_metrics = evaluate(
        ground_truth=GROUND_TRUTH,
        search_function=lambda query: engine.vector_search(query, num_results=5),
    )

    hybrid_metrics = evaluate(
        ground_truth=GROUND_TRUTH,
        search_function=lambda query: engine.hybrid_search(query, num_results=5),
    )

    print("Retrieval evaluation results")
    print("=" * 35)
    print_results("Text search", text_metrics)
    print_results("Vector search", vector_metrics)
    print_results("Hybrid search", hybrid_metrics)

    all_results = {
        "text": text_metrics,
        "vector": vector_metrics,
        "hybrid": hybrid_metrics,
    }

    best_method = max(
        all_results,
        key=lambda method: all_results[method]["mrr"],
    )

    print(f"Best retrieval method by MRR: {best_method}")


if __name__ == "__main__":
    main()
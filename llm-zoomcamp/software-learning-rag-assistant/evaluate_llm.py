from dataclasses import dataclass

from src.rag import RAGPipeline


@dataclass
class EvalCase:
    question: str
    expected_terms: list[str]


EVAL_CASES = [
    EvalCase(
        question="How do I debug Docker when localhost does not respond?",
        expected_terms=["docker", "localhost", "port"],
    ),
    EvalCase(
        question="What is RAG and when should I use it?",
        expected_terms=["retrieval", "context", "llm"],
    ),
    EvalCase(
        question="How do I evaluate retrieval quality?",
        expected_terms=["hit rate", "mrr", "ground truth"],
    ),
    EvalCase(
        question="What should I monitor in an LLM application?",
        expected_terms=["latency", "tokens", "feedback"],
    ),
    EvalCase(
        question="How should I structure a Python project?",
        expected_terms=["src", "tests", "readme"],
    ),
]


def score_answer(answer: str, sources: list[str], expected_terms: list[str]) -> float:
    answer_lower = answer.lower()

    term_hits = sum(1 for term in expected_terms if term.lower() in answer_lower)
    term_score = term_hits / len(expected_terms)

    has_sources_score = 1.0 if sources else 0.0

    length = len(answer.split())
    if 25 <= length <= 120:
        length_score = 1.0
    elif 10 <= length < 25 or 120 < length <= 180:
        length_score = 0.7
    else:
        length_score = 0.3

    return round(
        0.6 * term_score + 0.2 * has_sources_score + 0.2 * length_score,
        3,
    )


def evaluate_style(style: str) -> dict[str, float]:
    rag = RAGPipeline()

    scores = []

    for case in EVAL_CASES:
        response = rag.answer(
            question=case.question,
            retrieval_method="vector",
            num_results=4,
            use_reranking=True,
            style=style,
        )

        score = score_answer(
            answer=response.answer,
            sources=response.sources,
            expected_terms=case.expected_terms,
        )

        scores.append(score)

        print(f"Question: {case.question}")
        print(f"Style: {style}")
        print(f"Score: {score}")
        print(f"Sources: {response.sources}")
        print(f"Answer: {response.answer}")
        print("-" * 80)

    average_score = sum(scores) / len(scores)

    return {
        "average_score": round(average_score, 3),
    }


def main() -> None:
    print("LLM evaluation results")
    print("=" * 35)

    concise_metrics = evaluate_style("concise")
    detailed_metrics = evaluate_style("detailed")

    print("Summary")
    print("=" * 35)
    print(f"Concise average score:  {concise_metrics['average_score']:.3f}")
    print(f"Detailed average score: {detailed_metrics['average_score']:.3f}")

    if detailed_metrics["average_score"] > concise_metrics["average_score"]:
        best_style = "detailed"
    else:
        best_style = "concise"

    print(f"Best answer style: {best_style}")


if __name__ == "__main__":
    main()
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from gitsource import GithubRepositoryDataReader, chunk_documents
from minsearch import Index, VectorSearch
from tqdm import tqdm

from embedder import Embedder


Q1_EXPECTED_OPTION = 1400


def closest(value: float, options: list[float]) -> float:
    return min(options, key=lambda option: abs(option - value))


def load_documents() -> list[dict[str, Any]]:
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )

    return [file.parse() for file in reader.read()]


def load_ground_truth(path: str = "ground-truth.csv") -> list[dict[str, str]]:
    df = pd.read_csv(path)
    return df.to_dict(orient="records")


def build_text_index(chunks: list[dict[str, Any]]) -> Index:
    index = Index(
        text_fields=["content"],
        keyword_fields=["filename"],
    )
    index.fit(chunks)
    return index


def build_vector_index(
    embedder: Embedder,
    chunks: list[dict[str, Any]],
) -> tuple[VectorSearch, np.ndarray]:
    texts = [chunk["content"] for chunk in chunks]

    vectors = []
    batch_size = 32

    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding chunks"):
        batch = texts[i : i + batch_size]
        vectors.extend(embedder.encode_batch(batch))

    X = np.array(vectors)

    index = VectorSearch(keyword_fields=["filename"])
    index.fit(X, chunks)

    return index, X


def rrf(
    result_lists: list[list[dict[str, Any]]],
    k: int = 60,
    num_results: int = 5,
) -> list[dict[str, Any]]:
    scores = {}
    docs = {}

    for results in result_lists:
        for rank, doc in enumerate(results):
            key = (doc["filename"], doc["start"])
            scores[key] = scores.get(key, 0) + 1 / (k + rank)
            docs[key] = doc

    ranked = sorted(scores, key=scores.get, reverse=True)
    return [docs[key] for key in ranked[:num_results]]


def compute_relevance(
    ground_truth_record: dict[str, str],
    search_function: Callable[[str], list[dict[str, Any]]],
) -> list[int]:
    query = ground_truth_record["question"]
    expected_filename = ground_truth_record["filename"]

    results = search_function(query)

    return [
        int(result["filename"] == expected_filename)
        for result in results
    ]


def hit_rate(relevance_total: list[list[int]]) -> float:
    cnt = 0

    for line in relevance_total:
        if any(line):
            cnt += 1

    return cnt / len(relevance_total)


def mrr(relevance_total: list[list[int]]) -> float:
    total_score = 0.0

    for line in relevance_total:
        for rank, is_relevant in enumerate(line):
            if is_relevant:
                total_score += 1 / (rank + 1)
                break

    return total_score / len(relevance_total)


def evaluate(
    ground_truth: list[dict[str, str]],
    search_function: Callable[[str], list[dict[str, Any]]],
) -> dict[str, float]:
    relevance_total = []

    for record in tqdm(ground_truth, desc="Evaluating"):
        relevance = compute_relevance(record, search_function)
        relevance_total.append(relevance)

    return {
        "hit_rate": hit_rate(relevance_total),
        "mrr": mrr(relevance_total),
    }


def main() -> None:
    print("Loading documents...")
    documents = load_documents()
    print(f"Documents: {len(documents)}")

    print("\nChunking documents...")
    chunks = chunk_documents(documents, size=2000, step=1000)
    print(f"Chunks: {len(chunks)}")

    print("\nLoading ground truth...")
    ground_truth = load_ground_truth()
    print(f"Ground truth records: {len(ground_truth)}")

    print("\nLoading embedder...")
    embedder = Embedder()

    print("\nBuilding text index...")
    text_index = build_text_index(chunks)

    print("\nBuilding vector index...")
    vector_index, _ = build_vector_index(embedder, chunks)

    def text_search(query: str, num_results: int = 5) -> list[dict[str, Any]]:
        return text_index.search(query=query, num_results=num_results)

    def vector_search(query: str, num_results: int = 5) -> list[dict[str, Any]]:
        query_vector = np.array(embedder.encode(query))
        return vector_index.search(query_vector, num_results=num_results)

    def hybrid_search(query: str, k: int = 60) -> list[dict[str, Any]]:
        text_results = text_search(query, num_results=10)
        vector_results = vector_search(query, num_results=10)
        return rrf([text_results, vector_results], k=k, num_results=5)

    print("\nQ1. Generating questions")
    print("No API call is made in this script.")
    print(f"Expected closest option: {Q1_EXPECTED_OPTION}")

    first_question = ground_truth[0]["question"]
    print("\nFirst ground truth question:")
    print(first_question)

    print("\nQ2. First result with text search")
    q2_results = text_search(first_question)
    q2_answer = q2_results[0]["filename"]
    print("Answer:", q2_answer)

    print("\nQ3. First result with vector search")
    q3_results = vector_search(first_question)
    q3_answer = q3_results[0]["filename"]
    print("Answer:", q3_answer)

    print("\nQ4. Evaluating text search")
    text_metrics = evaluate(ground_truth, text_search)
    print("Text search metrics:", text_metrics)
    print("Closest hit rate option:", closest(text_metrics["hit_rate"], [0.55, 0.66, 0.76, 0.88]))

    print("\nQ5. Evaluating vector search")
    vector_metrics = evaluate(ground_truth, vector_search)
    print("Vector search metrics:", vector_metrics)
    print("Closest MRR option:", closest(vector_metrics["mrr"], [0.35, 0.45, 0.55, 0.65]))

    print("\nQ6. Tuning hybrid search")
    best_k = None
    best_mrr = -1.0

    for k in [1, 50, 100, 200]:
        metrics = evaluate(
            ground_truth,
            lambda query, k=k: hybrid_search(query, k=k),
        )
        current_mrr = metrics["mrr"]
        print(f"k={k}: {metrics}")

        if current_mrr > best_mrr:
            best_mrr = current_mrr
            best_k = k

    print("Best k:", best_k)


if __name__ == "__main__":
    main()
from collections import defaultdict
from typing import Any

import numpy as np
from gitsource import GithubRepositoryDataReader, chunk_documents
from minsearch import Index, VectorSearch
from tqdm import tqdm

from embedder import Embedder


QUERY_Q1 = "How does approximate nearest neighbor search work?"
QUERY_Q4 = "What metric do we use to evaluate a search engine?"
QUERY_Q5 = "How do I store vectors in PostgreSQL?"
QUERY_Q6 = "How do I give the model access to tools?"


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


def find_document(documents: list[dict[str, Any]], filename: str) -> dict[str, Any]:
    for doc in documents:
        if doc["filename"] == filename:
            return doc
    raise ValueError(f"Document not found: {filename}")


def embed_chunks(embedder: Embedder, chunks: list[dict[str, Any]]) -> np.ndarray:
    texts = [chunk["content"] for chunk in chunks]
    vectors = embedder.encode_batch(texts)
    return np.array(vectors)


def build_vector_index(vectors: np.ndarray, chunks: list[dict[str, Any]]) -> VectorSearch:
    index = VectorSearch(keyword_fields=["filename"])
    index.fit(vectors, chunks)
    return index


def build_text_index(chunks: list[dict[str, Any]]) -> Index:
    index = Index(
        text_fields=["content"],
        keyword_fields=["filename"],
    )
    index.fit(chunks)
    return index


def rrf(result_lists: list[list[dict[str, Any]]], k: int = 60, num_results: int = 5) -> list[dict[str, Any]]:
    scores = defaultdict(float)
    docs = {}

    for results in result_lists:
        for rank, doc in enumerate(results):
            key = (doc["filename"], doc.get("start", 0))
            scores[key] += 1 / (k + rank)
            docs[key] = doc

    ranked = sorted(scores, key=scores.get, reverse=True)
    return [docs[key] for key in ranked[:num_results]]


def print_results(title: str, results: list[dict[str, Any]]) -> None:
    print(f"\n{title}")
    for i, doc in enumerate(results, start=1):
        start = doc.get("start", "-")
        print(f"{i}. {doc['filename']} | start={start}")


def main() -> None:
    print("Loading embedder...")
    embedder = Embedder()

    print("\nQ1. Embedding a query")
    v = np.array(embedder.encode(QUERY_Q1))
    print(f"Raw value: {v[0]:.6f}")
    print("Answer option:", closest(float(v[0]), [-0.31, -0.02, 0.12, 0.44]))

    print("\nLoading documents...")
    documents = load_documents()
    print(f"Documents: {len(documents)}")

    print("\nQ2. Cosine similarity")
    target_doc = find_document(
        documents,
        "02-vector-search/lessons/07-sqlitesearch-vector.md",
    )
    target_vector = np.array(embedder.encode(target_doc["content"]))
    similarity = float(target_vector.dot(v))
    print(f"Raw value: {similarity:.6f}")
    print("Answer option:", closest(similarity, [0.07, 0.37, 0.68, 0.92]))

    print("\nChunking documents...")
    chunks = chunk_documents(documents, size=2000, step=1000)
    print(f"Chunks: {len(chunks)}")

    print("\nEmbedding chunks...")
    X = embed_chunks(embedder, chunks)

    print("\nQ3. Chunking and search by hand")
    scores = X.dot(v)
    best_idx = int(np.argmax(scores))
    best_chunk = chunks[best_idx]
    print(f"Raw score: {scores[best_idx]:.6f}")
    print("Answer:", best_chunk["filename"])

    print("\nBuilding vector index...")
    vector_index = build_vector_index(X, chunks)

    print("\nQ4. Vector search with minsearch")
    q4_vector = np.array(embedder.encode(QUERY_Q4))
    q4_results = vector_index.search(q4_vector, num_results=5)
    print_results("Q4 vector results", q4_results)
    print("Answer:", q4_results[0]["filename"])

    print("\nBuilding text index...")
    text_index = build_text_index(chunks)

    print("\nQ5. Text search vs vector search")
    q5_vector = np.array(embedder.encode(QUERY_Q5))
    q5_vector_results = vector_index.search(q5_vector, num_results=5)
    q5_text_results = text_index.search(QUERY_Q5, num_results=5)

    print_results("Q5 vector results", q5_vector_results)
    print_results("Q5 text results", q5_text_results)

    vector_files = {doc["filename"] for doc in q5_vector_results}
    text_files = {doc["filename"] for doc in q5_text_results}
    vector_only = vector_files - text_files

    print("Vector-only files:")
    for filename in sorted(vector_only):
        print("-", filename)

    print("\nQ6. Hybrid search")
    q6_vector = np.array(embedder.encode(QUERY_Q6))
    q6_vector_results = vector_index.search(q6_vector, num_results=5)
    q6_text_results = text_index.search(QUERY_Q6, num_results=5)
    q6_hybrid_results = rrf([q6_vector_results, q6_text_results])

    print_results("Q6 vector results", q6_vector_results)
    print_results("Q6 text results", q6_text_results)
    print_results("Q6 hybrid results", q6_hybrid_results)

    print("Answer:", q6_hybrid_results[0]["filename"])


if __name__ == "__main__":
    main()
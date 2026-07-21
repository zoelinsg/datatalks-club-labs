import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.config import CHUNKS_PATH


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run `poetry run python ingest.py` first."
        )

    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(text: str) -> list[str]:
    """Simple tokenizer for technical notes."""
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def cosine_score(query_vector: dict[str, float], doc_vector: dict[str, float]) -> float:
    common_terms = set(query_vector).intersection(doc_vector)

    dot_product = sum(query_vector[term] * doc_vector[term] for term in common_terms)

    query_norm = math.sqrt(sum(value * value for value in query_vector.values()))
    doc_norm = math.sqrt(sum(value * value for value in doc_vector.values()))

    if query_norm == 0 or doc_norm == 0:
        return 0.0

    return dot_product / (query_norm * doc_norm)


class SearchEngine:
    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks
        self.doc_tokens = self._build_doc_tokens(chunks)
        self.idf = self._build_idf(self.doc_tokens)
        self.doc_vectors = self._build_doc_vectors(self.doc_tokens)

    def _build_doc_tokens(self, chunks: list[dict[str, Any]]) -> list[list[str]]:
        tokenized_docs = []

        for chunk in chunks:
            text = f"{chunk['title']} {chunk['content']}"
            tokenized_docs.append(tokenize(text))

        return tokenized_docs

    def _build_idf(self, tokenized_docs: list[list[str]]) -> dict[str, float]:
        document_count = len(tokenized_docs)
        document_frequency = defaultdict(int)

        for tokens in tokenized_docs:
            for term in set(tokens):
                document_frequency[term] += 1

        idf = {}

        for term, frequency in document_frequency.items():
            idf[term] = math.log((document_count + 1) / (frequency + 1)) + 1

        return idf

    def _to_tfidf_vector(self, tokens: list[str]) -> dict[str, float]:
        term_counts = Counter(tokens)
        total_terms = sum(term_counts.values())

        if total_terms == 0:
            return {}

        vector = {}

        for term, count in term_counts.items():
            tf = count / total_terms
            vector[term] = tf * self.idf.get(term, 1.0)

        return vector

    def _build_doc_vectors(
        self,
        tokenized_docs: list[list[str]],
    ) -> list[dict[str, float]]:
        return [self._to_tfidf_vector(tokens) for tokens in tokenized_docs]

    def text_search(self, query: str, num_results: int = 5) -> list[dict[str, Any]]:
        """
        Keyword-style search.

        Scores exact keyword overlap and gives more weight to title matches.
        """
        query_terms = tokenize(query)
        query_counter = Counter(query_terms)

        scored_results = []

        for chunk, tokens in zip(self.chunks, self.doc_tokens):
            token_counter = Counter(tokens)
            title_terms = set(tokenize(chunk["title"]))

            score = 0.0

            for term, query_count in query_counter.items():
                content_match = token_counter.get(term, 0)
                title_match = 1 if term in title_terms else 0

                score += query_count * content_match
                score += 3.0 * title_match

            if score > 0:
                scored_results.append(
                    {
                        **chunk,
                        "score": float(score),
                        "retrieval_method": "text",
                    }
                )

        scored_results.sort(key=lambda item: item["score"], reverse=True)

        return scored_results[:num_results]

    def vector_search(self, query: str, num_results: int = 5) -> list[dict[str, Any]]:
        """
        Local TF-IDF cosine search.

        This is a lightweight vector-like retrieval method that does not require
        scikit-learn, sentence-transformers, or external model downloads.
        """
        query_tokens = tokenize(query)
        query_vector = self._to_tfidf_vector(query_tokens)

        scored_results = []

        for chunk, doc_vector in zip(self.chunks, self.doc_vectors):
            score = cosine_score(query_vector, doc_vector)

            if score > 0:
                scored_results.append(
                    {
                        **chunk,
                        "score": float(score),
                        "retrieval_method": "vector",
                    }
                )

        scored_results.sort(key=lambda item: item["score"], reverse=True)

        return scored_results[:num_results]

    def hybrid_search(
        self,
        query: str,
        num_results: int = 5,
        rrf_k: int = 60,
    ) -> list[dict[str, Any]]:
        text_results = self.text_search(query, num_results=10)
        vector_results = self.vector_search(query, num_results=10)

        return reciprocal_rank_fusion(
            result_lists=[text_results, vector_results],
            k=rrf_k,
            num_results=num_results,
        )


def reciprocal_rank_fusion(
    result_lists: list[list[dict[str, Any]]],
    k: int = 60,
    num_results: int = 5,
) -> list[dict[str, Any]]:
    scores = {}
    docs = {}

    for results in result_lists:
        for rank, doc in enumerate(results):
            key = doc["id"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
            docs[key] = doc

    ranked_keys = sorted(scores, key=scores.get, reverse=True)

    fused_results = []

    for key in ranked_keys[:num_results]:
        doc = docs[key]
        fused_results.append(
            {
                **doc,
                "score": float(scores[key]),
                "retrieval_method": "hybrid",
            }
        )

    return fused_results


def simple_rerank(query: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Lightweight reranking based on query keyword overlap.
    """
    query_terms = set(tokenize(query))

    reranked = []

    for doc in results:
        content_terms = set(tokenize(doc["content"]))
        overlap = len(query_terms.intersection(content_terms))

        rerank_score = doc["score"] + math.log1p(overlap)

        reranked.append(
            {
                **doc,
                "rerank_score": float(rerank_score),
            }
        )

    return sorted(reranked, key=lambda item: item["rerank_score"], reverse=True)


def build_search_engine() -> SearchEngine:
    chunks = load_chunks()
    return SearchEngine(chunks)


if __name__ == "__main__":
    engine = build_search_engine()

    query = "How do I debug Docker when localhost does not respond?"

    print(f"Query: {query}")

    print("\nText search:")
    for result in engine.text_search(query, num_results=3):
        print("-", result["source"], result["score"])

    print("\nVector search:")
    for result in engine.vector_search(query, num_results=3):
        print("-", result["source"], result["score"])

    print("\nHybrid search with reranking:")
    hybrid_results = engine.hybrid_search(query, num_results=5)
    reranked_results = simple_rerank(query, hybrid_results)

    for result in reranked_results[:3]:
        print("-", result["source"], result["rerank_score"])
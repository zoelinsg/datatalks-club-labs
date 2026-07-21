import re
import time
from dataclasses import dataclass
from typing import Any

from src.search import SearchEngine, build_search_engine, simple_rerank


@dataclass
class RAGResponse:
    question: str
    answer: str
    sources: list[str]
    retrieval_method: str
    latency_ms: float
    context: str


class MockLLM:
    """
    Local mock LLM.

    This keeps the project runnable without OpenAI, Gemini, or Ollama.
    The answer is generated from retrieved context using simple extractive logic.
    """

    def generate(self, question: str, context: str, style: str = "concise") -> str:
        sentences = self._extract_relevant_sentences(question, context)

        if not sentences:
            return (
                "I could not find enough relevant information in the knowledge base "
                "to answer this question confidently."
            )

        if style == "detailed":
            selected = sentences[:5]
            intro = "Based on the engineering notes, here is a detailed answer:"
        else:
            selected = sentences[:3]
            intro = "Based on the engineering notes:"

        answer_body = " ".join(selected)

        return f"{intro}\n\n{answer_body}"

    def _extract_relevant_sentences(self, question: str, context: str) -> list[str]:
        question_terms = set(re.findall(r"[a-zA-Z0-9_]+", question.lower()))

        cleaned_context = context

        # Remove source markers such as [Source 1: docker_troubleshooting.md]
        cleaned_context = re.sub(r"\[Source \d+: .*?\]", " ", cleaned_context)

        # Remove markdown headings and common markdown symbols
        cleaned_context = re.sub(r"#+\s*", " ", cleaned_context)
        cleaned_context = cleaned_context.replace("`", "")
        cleaned_context = cleaned_context.replace("-", " ")

        # Preserve sentence boundaries better
        raw_sentences = re.split(r"(?<=[.!?])\s+", cleaned_context.replace("\n", " "))

        scored_sentences = []

        for sentence in raw_sentences:
            sentence = re.sub(r"\s+", " ", sentence).strip()

            if len(sentence) < 25:
                continue

            sentence_terms = set(re.findall(r"[a-zA-Z0-9_]+", sentence.lower()))
            overlap = len(question_terms.intersection(sentence_terms))

            # Give Docker / troubleshooting sentences a small boost when relevant
            if "docker" in question_terms and "docker" in sentence_terms:
                overlap += 2

            if "localhost" in question_terms and "localhost" in sentence_terms:
                overlap += 2

            if overlap > 0:
                scored_sentences.append((overlap, sentence))

        scored_sentences.sort(key=lambda item: item[0], reverse=True)

        return [sentence for _, sentence in scored_sentences]


class RAGPipeline:
    def __init__(self, search_engine: SearchEngine | None = None):
        self.search_engine = search_engine or build_search_engine()
        self.llm = MockLLM()

    def build_context(self, results: list[dict[str, Any]]) -> str:
        context_blocks = []

        for index, result in enumerate(results, start=1):
            context_blocks.append(
                f"[Source {index}: {result['source']}]\n{result['content']}"
            )

        return "\n\n".join(context_blocks)

    def answer(
        self,
        question: str,
        retrieval_method: str = "hybrid",
        num_results: int = 4,
        use_reranking: bool = True,
        style: str = "concise",
    ) -> RAGResponse:
        start_time = time.perf_counter()

        if retrieval_method == "text":
            results = self.search_engine.text_search(question, num_results=num_results)
        elif retrieval_method == "vector":
            results = self.search_engine.vector_search(question, num_results=num_results)
        elif retrieval_method == "hybrid":
            results = self.search_engine.hybrid_search(question, num_results=num_results)
        else:
            raise ValueError(
                "retrieval_method must be one of: text, vector, hybrid"
            )

        if use_reranking:
            results = simple_rerank(question, results)

        context = self.build_context(results)
        answer = self.llm.generate(question=question, context=context, style=style)

        latency_ms = (time.perf_counter() - start_time) * 1000

        sources = []
        for result in results:
            if result["source"] not in sources:
                sources.append(result["source"])

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieval_method=retrieval_method,
            latency_ms=latency_ms,
            context=context,
        )


if __name__ == "__main__":
    rag = RAGPipeline()

    question = "How do I debug Docker when localhost does not respond?"

    response = rag.answer(
        question=question,
        retrieval_method="hybrid",
        use_reranking=True,
        style="concise",
    )

    print("Question:")
    print(response.question)

    print("\nAnswer:")
    print(response.answer)

    print("\nSources:")
    for source in response.sources:
        print("-", source)

    print(f"\nLatency: {response.latency_ms:.2f} ms")
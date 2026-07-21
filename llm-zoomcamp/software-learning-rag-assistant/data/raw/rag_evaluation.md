# RAG Evaluation

RAG systems should be evaluated systematically instead of judged only by intuition.

Retrieval evaluation checks whether the search step returns the correct documents. Common retrieval metrics include Hit Rate and Mean Reciprocal Rank.

Hit Rate measures whether at least one relevant document appears in the top results. MRR rewards systems that rank the correct result higher.

To evaluate retrieval, create a ground truth dataset with questions and expected source documents. Each search method can then be tested against the same dataset.

LLM evaluation checks the quality of the final generated answer. It can be done manually, with user feedback, or with another LLM acting as a judge.

A good evaluation process compares multiple approaches. For example, compare text search, vector search, and hybrid search. Then choose the method with the best metrics.

Evaluation should be repeatable. The same test set should be used when tuning chunk size, search boosts, prompts, or reranking logic.

Evaluation helps replace guessing with measurement.
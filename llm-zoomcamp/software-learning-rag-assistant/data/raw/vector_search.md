# Vector Search

Vector search represents text as numeric embeddings. Texts with similar meaning should have embeddings that are close together in vector space.

A vector search system usually works like this:

1. Convert document chunks into embeddings
2. Store the embeddings in a vector index
3. Convert the user query into an embedding
4. Compare the query embedding with document embeddings
5. Return the most similar chunks

Cosine similarity is commonly used to compare embeddings. It measures the angle between vectors rather than their raw size.

Vector search is good for semantic matching. It can find relevant documents even when the query uses different words from the document. For example, a query about "container startup command" may still match a document that talks about Docker `CMD`.

Text search is good for exact keyword matching. It works well when the user query contains specific terms, function names, error messages, file names, or command-line output.

Hybrid search combines text search and vector search. It is often better than either method alone because it captures both exact matching and semantic similarity.

Reranking can be used after retrieval to reorder candidate chunks. A reranker looks more carefully at the query and each candidate result.

In a RAG application, vector search is useful because users often ask questions in different wording from the source documents. However, vector search can sometimes miss exact technical keywords, so evaluating it against text search and hybrid search is important.
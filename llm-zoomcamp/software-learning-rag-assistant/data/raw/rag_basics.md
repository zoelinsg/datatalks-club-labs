# RAG Basics

Retrieval Augmented Generation, or RAG, improves LLM answers by providing relevant external context.

A basic RAG system has four steps:

1. Load documents
2. Split documents into chunks
3. Retrieve relevant chunks for a user query
4. Send the query and retrieved context to an LLM

RAG helps when the model does not know private, recent, or domain-specific information. Instead of relying only on training data, the model answers using retrieved documents.

The quality of a RAG system depends heavily on retrieval. If the retrieved context is wrong or incomplete, the final answer is likely to be wrong.

Chunking is important because documents are often too long to send directly to an LLM. Chunks should be large enough to preserve meaning but small enough to retrieve precise information.

A prompt should clearly separate the user question from the retrieved context. It should also tell the model to answer only using the provided context when accuracy matters.

RAG is useful for documentation assistants, internal knowledge bases, support bots, research assistants, and learning tools.
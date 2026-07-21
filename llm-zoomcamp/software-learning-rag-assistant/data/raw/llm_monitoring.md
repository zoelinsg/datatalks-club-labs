# LLM Application Monitoring

Monitoring helps understand how an LLM application behaves after real users start using it.

Useful metrics include:

- number of user queries
- response latency
- input tokens
- output tokens
- estimated cost
- user feedback
- error rate

For RAG systems, monitoring can also record retrieved documents, search scores, and whether the user found the answer helpful.

A simple monitoring setup can store logs in SQLite. Each interaction can include the timestamp, user question, generated answer, latency, feedback, and retrieval method.

A dashboard helps developers see trends over time. Useful charts include query volume, average latency, feedback distribution, token usage, top questions, and retrieval method usage.

Monitoring is different from offline evaluation. Offline evaluation uses a fixed dataset before deployment. Monitoring observes real usage after deployment.

Both are important. Evaluation helps choose a better system design. Monitoring helps detect problems in production.
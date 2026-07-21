import streamlit as st

from src.feedback import save_negative_feedback, save_positive_feedback
from src.monitoring import log_interaction
from src.rag import RAGPipeline


st.set_page_config(
    page_title="Software Engineering Learning Notes Assistant",
    page_icon="SE",
    layout="wide",
)


@st.cache_resource
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline()


def render_feedback(interaction_id: int) -> None:
    st.subheader("Feedback")
    st.write("Was this answer helpful?")

    feedback_col1, feedback_col2 = st.columns(2)

    with feedback_col1:
        if st.button("Helpful", key=f"positive_{interaction_id}"):
            save_positive_feedback(interaction_id)
            st.success("Thanks for your feedback.")

    with feedback_col2:
        if st.button("Not helpful", key=f"negative_{interaction_id}"):
            save_negative_feedback(interaction_id)
            st.warning("Thanks. This feedback will help improve the assistant.")


def main() -> None:
    st.title("Software Engineering Learning Notes Assistant")
    st.write(
        "Ask questions about Python project structure, Docker, RAG, "
        "vector search, evaluation, monitoring, and debugging."
    )

    rag = get_rag_pipeline()

    with st.sidebar:
        st.header("Settings")

        retrieval_method = st.selectbox(
            "Retrieval method",
            options=["vector", "hybrid", "text"],
            index=0,
        )

        style = st.selectbox(
            "Answer style",
            options=["detailed", "concise"],
            index=0,
        )

        num_results = st.slider(
            "Number of retrieved chunks",
            min_value=1,
            max_value=6,
            value=4,
        )

        use_reranking = st.checkbox(
            "Use reranking",
            value=True,
        )

        st.divider()

        st.caption(
            "This demo uses a local mock LLM, so it runs without OpenAI, "
            "Gemini, or Ollama credentials."
        )

    example_questions = [
        "How do I structure a Python project?",
        "What is the difference between a Docker image and a container?",
        "How do I debug Docker when localhost does not respond?",
        "What is RAG and when should I use it?",
        "How do I evaluate retrieval quality?",
        "What should I monitor in an LLM application?",
    ]

    question = st.text_input(
        "Your question",
        value=example_questions[2],
        placeholder="Ask a software engineering question...",
    )

    if "last_response" not in st.session_state:
        st.session_state.last_response = None

    if "last_interaction_key" not in st.session_state:
        st.session_state.last_interaction_key = None

    if "last_interaction_id" not in st.session_state:
        st.session_state.last_interaction_id = None

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Searching notes and generating an answer..."):
            response = rag.answer(
                question=question,
                retrieval_method=retrieval_method,
                num_results=num_results,
                use_reranking=use_reranking,
                style=style,
            )

        interaction_key = (
            f"{response.question}_"
            f"{response.retrieval_method}_"
            f"{style}_"
            f"{num_results}_"
            f"{use_reranking}"
        )

        if st.session_state.last_interaction_key != interaction_key:
            interaction_id = log_interaction(
                question=response.question,
                answer=response.answer,
                sources=response.sources,
                retrieval_method=response.retrieval_method,
                latency_ms=response.latency_ms,
            )

            st.session_state.last_interaction_id = interaction_id
            st.session_state.last_interaction_key = interaction_key

        st.session_state.last_response = response

    response = st.session_state.last_response
    interaction_id = st.session_state.last_interaction_id

    if response is not None:
        st.subheader("Answer")
        st.write(response.answer)

        st.subheader("Sources")
        for source in response.sources:
            st.markdown(f"- `{source}`")

        if interaction_id is not None:
            render_feedback(interaction_id)

        st.subheader("Run details")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Retrieval method", response.retrieval_method)

        with col2:
            st.metric("Sources used", len(response.sources))

        with col3:
            st.metric("Latency", f"{response.latency_ms:.2f} ms")

        with st.expander("Retrieved context"):
            st.text(response.context)

    st.divider()

    st.subheader("Example questions")
    for item in example_questions:
        st.markdown(f"- {item}")


if __name__ == "__main__":
    main()
import json

import pandas as pd
import streamlit as st

from src.monitoring import fetch_interactions


st.set_page_config(
    page_title="Monitoring Dashboard",
    page_icon="MD",
    layout="wide",
)


def load_data() -> pd.DataFrame:
    rows = fetch_interactions()

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df["sources_count"] = df["sources"].apply(lambda value: len(json.loads(value)))
    df["question_length"] = df["question"].str.len()
    df["answer_length"] = df["answer"].str.len()

    return df


def main() -> None:
    st.title("Monitoring Dashboard")
    st.write(
        "This dashboard summarizes logged interactions from the "
        "Software Engineering Learning Notes Assistant."
    )

    df = load_data()

    if df.empty:
        st.warning("No interaction logs found yet. Ask a question in app.py first.")
        return

    total_queries = len(df)
    avg_latency = df["latency_ms"].mean()
    feedback_count = df["feedback"].notna().sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total queries", total_queries)

    with col2:
        st.metric("Average latency", f"{avg_latency:.2f} ms")

    with col3:
        st.metric("Feedback count", feedback_count)

    st.divider()

    st.subheader("Chart 1: Queries over time")
    queries_by_date = df.groupby("date").size().reset_index(name="queries")
    st.bar_chart(queries_by_date, x="date", y="queries")

    st.subheader("Chart 2: Average latency by retrieval method")
    latency_by_method = (
        df.groupby("retrieval_method")["latency_ms"]
        .mean()
        .reset_index()
    )
    st.bar_chart(latency_by_method, x="retrieval_method", y="latency_ms")

    st.subheader("Chart 3: Feedback distribution")
    feedback_distribution = (
        df["feedback"]
        .fillna("missing")
        .value_counts()
        .reset_index()
    )
    feedback_distribution.columns = ["feedback", "count"]
    st.bar_chart(feedback_distribution, x="feedback", y="count")

    st.subheader("Chart 4: Sources used per query")
    st.bar_chart(df[["id", "sources_count"]], x="id", y="sources_count")

    st.subheader("Chart 5: Question length over interactions")
    st.line_chart(df[["id", "question_length"]], x="id", y="question_length")

    st.subheader("Chart 6: Answer length over interactions")
    st.line_chart(df[["id", "answer_length"]], x="id", y="answer_length")

    st.subheader("Recent interactions")
    display_columns = [
        "timestamp",
        "question",
        "retrieval_method",
        "latency_ms",
        "feedback",
    ]
    st.dataframe(df[display_columns], width="stretch")


if __name__ == "__main__":
    main()
import duckdb


DB_PATH = "local_agent_traces.duckdb"
SCHEMA = "agent_traces"


def main() -> None:
    con = duckdb.connect(DB_PATH)

    print("Q1. Span count for one agent run")
    span_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM {SCHEMA}.spans
        """
    ).fetchone()[0]
    print("Span count:", span_count)

    print("\nQ2. Number of tables created by dlt")
    table_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA}'
        """
    ).fetchone()[0]
    print("Table count:", table_count)

    print("\nTables:")
    tables = con.execute(
        f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA}'
        ORDER BY table_name
        """
    ).fetchall()

    for table in tables:
        print("-", table[0])

    print("\nQ3. Total input tokens for the agent run")
    total_input_tokens = con.execute(
        f"""
        SELECT SUM(gen_ai_usage_input_tokens)
        FROM {SCHEMA}.spans
        """
    ).fetchone()[0]
    print("Total input tokens:", total_input_tokens)

    print("\nAnswer candidates")
    print("Q1:", span_count)
    print("Q2:", table_count)
    print("Q3: 10000 - 20000")


if __name__ == "__main__":
    main()
import json
import sqlite3
from datetime import datetime
from typing import Any

from src.config import APP_LOGS_PATH


DB_PATH = APP_LOGS_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT NOT NULL,
                retrieval_method TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                feedback TEXT
            )
            """
        )


def log_interaction(
    question: str,
    answer: str,
    sources: list[str],
    retrieval_method: str,
    latency_ms: float,
) -> int:
    init_db()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO interactions (
                timestamp,
                question,
                answer,
                sources,
                retrieval_method,
                latency_ms,
                feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                question,
                answer,
                json.dumps(sources, ensure_ascii=False),
                retrieval_method,
                latency_ms,
                None,
            ),
        )

        return int(cursor.lastrowid)


def update_feedback(interaction_id: int, feedback: str) -> None:
    init_db()

    if feedback not in {"positive", "negative"}:
        raise ValueError("feedback must be either 'positive' or 'negative'")

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE interactions
            SET feedback = ?
            WHERE id = ?
            """,
            (feedback, interaction_id),
        )


def fetch_interactions() -> list[dict[str, Any]]:
    init_db()

    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT *
            FROM interactions
            ORDER BY timestamp DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
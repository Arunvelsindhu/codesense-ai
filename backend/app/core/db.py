import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone

from app.core.config import settings


def _ensure_parent_dir():
    parent = os.path.dirname(settings.sqlite_db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


@contextmanager
def get_connection():
    _ensure_parent_dir()
    conn = sqlite3.connect(settings.sqlite_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                repo_name TEXT PRIMARY KEY,
                repo_url TEXT,
                analyzed_at TEXT NOT NULL,
                total_chunks INTEGER DEFAULT 0,
                chunks_embedded INTEGER DEFAULT 0,
                readme TEXT,
                code_issues_summary TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_repo
            ON chat_messages(repo_name)
        """)


def upsert_repo_analysis(repo_name: str, repo_url: str, result: dict):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO repos (repo_name, repo_url, analyzed_at, total_chunks, chunks_embedded, readme, code_issues_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repo_name) DO UPDATE SET
                repo_url=excluded.repo_url,
                analyzed_at=excluded.analyzed_at,
                total_chunks=excluded.total_chunks,
                chunks_embedded=excluded.chunks_embedded,
                readme=excluded.readme,
                code_issues_summary=excluded.code_issues_summary
        """, (
            repo_name,
            repo_url,
            datetime.now(timezone.utc).isoformat(),
            result.get("total_chunks", 0),
            result.get("chunks_embedded", 0),
            result.get("readme"),
            result.get("code_issues_summary"),
        ))


def get_repo_analysis(repo_name: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM repos WHERE repo_name = ?", (repo_name,)
        ).fetchone()
        return dict(row) if row else None


def list_repos() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT repo_name, repo_url, analyzed_at, total_chunks, chunks_embedded FROM repos ORDER BY analyzed_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_repo(repo_name: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM repos WHERE repo_name = ?", (repo_name,))
        conn.execute("DELETE FROM chat_messages WHERE repo_name = ?", (repo_name,))


def add_chat_message(repo_name: str, role: str, text: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_messages (repo_name, role, text, created_at) VALUES (?, ?, ?, ?)",
            (repo_name, role, text, datetime.now(timezone.utc).isoformat()),
        )


def get_chat_history(repo_name: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, text, created_at FROM chat_messages WHERE repo_name = ? ORDER BY id ASC",
            (repo_name,),
        ).fetchall()
        return [dict(row) for row in rows]

"""Read-only bridge into claude-mem's SQLite store.

claude-mem owns its own database and worker process; goldfish never writes to it
and never runs claude-mem's own hooks/workers. This module only opens the DB
file in read-only mode (`mode=ro`) to surface recent session context alongside
brain's transcript search and memory_notes' curated facts, so one MCP server
can answer "what have we been doing" without the caller needing to know which
of the three backing stores has the answer.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def _connect_ro(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{db_path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def is_available(db_path: Path) -> bool:
    return db_path.exists()


def recent_session_summaries(db_path: Path, limit: int = 10) -> list[dict[str, Any]]:
    if not is_available(db_path):
        return []
    con = _connect_ro(db_path)
    try:
        con.row_factory = sqlite3.Row
        cols = {row[1] for row in con.execute("PRAGMA table_info(session_summaries)")}
        order_col = "created_at" if "created_at" in cols else "id"
        rows = con.execute(
            f"SELECT * FROM session_summaries ORDER BY {order_col} DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()


def search_observations(db_path: Path, query: str, limit: int = 20) -> list[dict[str, Any]]:
    if not is_available(db_path):
        return []
    con = _connect_ro(db_path)
    try:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM observations WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        con.close()

"""
Thin DB helper. SQLite by default; swap to Postgres by setting DATABASE_URL.

Why so minimal? Week 6-7 intern shouldn't need to learn SQLAlchemy ORM
internals. Raw queries via pandas / sqlite3 keep the API code readable.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = ROOT / "capstone.db"


def db_path() -> Path:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", "", 1))
    return DEFAULT_SQLITE_PATH


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

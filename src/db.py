\
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Any

def connect(db_path: str | Path) -> sqlite3.Connection:
    db_path = str(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def execmany(conn: sqlite3.Connection, sql: str, rows: Iterable[Iterable[Any]]) -> None:
    conn.executemany(sql, rows)
    conn.commit()

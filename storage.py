"""Хранение заявок в SQLite.

Telegram-уведомление — основной канал доставки лида, база — страховка:
если мастер пролистал чат, заявку всегда можно достать командой /leads.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    tg_user_id  INTEGER NOT NULL,
    tg_username TEXT,
    lang        TEXT    NOT NULL,
    service     TEXT,
    segment     TEXT,
    geo         TEXT,
    area        TEXT,
    timing      TEXT,
    budget      TEXT,
    name        TEXT,
    contact     TEXT,
    score       INTEGER NOT NULL DEFAULT 0,
    status      TEXT    NOT NULL DEFAULT 'new'
);
"""


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as conn:
        conn.executescript(SCHEMA)


def save_lead(data: dict[str, Any]) -> int:
    """Возвращает номер заявки — он же попадает в уведомление мастеру."""
    fields = (
        "created_at", "tg_user_id", "tg_username", "lang", "service", "segment",
        "geo", "area", "timing", "budget", "name", "contact", "score", "status",
    )
    row = {f: data.get(f) for f in fields}
    row["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    placeholders = ", ".join(f":{f}" for f in fields)
    with _conn() as conn:
        cur = conn.execute(
            f"INSERT INTO leads ({', '.join(fields)}) VALUES ({placeholders})", row
        )
        return int(cur.lastrowid)


def recent_leads(limit: int = 10) -> list[sqlite3.Row]:
    with _conn() as conn:
        return list(
            conn.execute(
                "SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        )


def stats() -> dict[str, int]:
    with _conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        by_status = dict(
            conn.execute(
                "SELECT status, COUNT(*) FROM leads GROUP BY status"
            ).fetchall()
        )
    return {"total": total, **by_status}

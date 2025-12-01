import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "dados.db")

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _get_conn() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                ts   INTEGER NOT NULL,
                packet_number TEXT,
                node_id TEXT NOT NULL DEFAULT 'node_padrao',
                temp REAL,
                rh   REAL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS ix_packet_ts ON readings(packet_number, ts)"
        )

def migrate_db():
    pass

def insert_reading(
    ts: int,
    packet_number: Optional[str],
    node_id: Optional[str] = "node_padrao",
    temp: Any = None,
    rh: Any = None,
):
    if node_id is None:
        node_id = "node_padrao"

    with _get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO readings (ts, packet_number, node_id, temp, rh)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ts, packet_number, node_id, temp, rh),
        )

def delete_all():
    with _get_conn() as conn:
        conn.execute("DELETE FROM readings")

def get_last_readings(limit: int = 50, packet_number: Optional[str] = None) -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.cursor()
        if packet_number:
            cur.execute(
                "SELECT * FROM readings WHERE packet_number = ? ORDER BY ts DESC LIMIT ?",
                (packet_number, limit),
            )
        else:
            cur.execute(
                "SELECT * FROM readings ORDER BY ts DESC LIMIT ?",
                (limit,),
            )
        return [dict(r) for r in cur.fetchall()]

def get_latest_by_packet() -> Dict[str, Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.*
            FROM readings r
            JOIN (
                SELECT packet_number, MAX(ts) AS max_ts
                FROM readings
                GROUP BY packet_number
            ) x
            ON r.packet_number = x.packet_number AND r.ts = x.max_ts
            """
        )
        return {row["packet_number"]: dict(row) for row in cur.fetchall()}

def count_rows() -> int:
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM readings")
        return int(cur.fetchone()[0])
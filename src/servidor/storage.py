"""
Persistência SQLite com conexões separadas para LEITURA e ESCRITA.
Evita 'database is locked' em cenários multi-thread.
"""

import sqlite3
import os
import threading
from typing import Any, Dict, List, Optional

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "dados.db")

# Conexões separadas
_write_conn: Optional[sqlite3.Connection] = None
_read_conn: Optional[sqlite3.Connection] = None

# Mutex apenas para escrita
_write_lock = threading.Lock()


# -------- Funções internas --------

def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")  # aguarda 5s antes de dar locked
    return conn


def _get_write_conn() -> sqlite3.Connection:
    global _write_conn
    if _write_conn is None:
        _write_conn = _make_conn()
    return _write_conn


def _get_read_conn() -> sqlite3.Connection:
    global _read_conn
    if _read_conn is None:
        _read_conn = _make_conn()
    return _read_conn


# -------- Inicialização --------

def init_db():
    conn = _get_write_conn()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                ts   INTEGER NOT NULL,
                packet_number TEXT,
                temp REAL,
                rh   REAL
            )
        """)


def migrate_db():
    conn = _get_write_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(readings)")
    cols = [row[1] for row in cur.fetchall()]

    if "packet_number" not in cols:
        cur.execute("ALTER TABLE readings ADD COLUMN packet_number TEXT")

    cur.execute("""
        CREATE INDEX IF NOT EXISTS ix_packet_number_ts
        ON readings(packet_number, ts)
    """)

    conn.commit()


# -------- ESCRITA --------

def insert_reading(ts: int, packet_number: str, temp: Any = None, rh: Any = None):
    conn = _get_write_conn()
    with _write_lock:
        conn.execute(
            """
            INSERT OR REPLACE INTO readings (ts, packet_number, temp, rh)
            VALUES (?, ?, ?, ?)
        """,
            (ts, packet_number, temp, rh),
        )
        conn.commit()


def delete_all():
    conn = _get_write_conn()
    with _write_lock:
        conn.execute("DELETE FROM readings")
        conn.commit()


# -------- LEITURA --------

def get_last_readings(limit: int = 50, packet_number: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_read_conn()
    cur = conn.cursor()
    if packet_number:
        cur.execute(
            """
            SELECT ts, packet_number, temp, rh
            FROM readings
            WHERE packet_number = ?
            ORDER BY ts DESC
            LIMIT ?
        """,
            (packet_number, limit),
        )
    else:
        cur.execute(
            """
            SELECT ts, packet_number, temp, rh
            FROM readings
            ORDER BY ts DESC
            LIMIT ?
        """,
            (limit,),
        )
    return [dict(r) for r in cur.fetchall()]


def get_latest_by_packet() -> Dict[str, Dict[str, Any]]:
    conn = _get_read_conn()
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
        ORDER BY r.packet_number
    """
    )
    return {row["packet_number"]: dict(row) for row in cur.fetchall()}


def get_last_readings_for_packet(packet_number: str, limit: int = 20):
    conn = _get_read_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ts, temp, rh
        FROM readings
        WHERE packet_number = ?
        ORDER BY ts DESC
        LIMIT ?
        """,
        (packet_number, limit),
    )
    rows = cur.fetchall()
    return [dict(r) for r in rows][::-1]


def count_rows() -> int:
    conn = _get_read_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM readings")
    return int(cur.fetchone()[0])

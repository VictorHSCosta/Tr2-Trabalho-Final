"""
Abstração simples de persistência em SQLite (stdlib).
- init_db() : cria o banco e índices
- insert_reading(...) : insere uma leitura
- get_last_readings(limit, room_id) : últimas leituras
- get_latest_by_room() : última leitura por sala
- count_rows() : total de linhas (para métricas)
"""

import sqlite3
import os
import threading
from typing import Any, Dict, List, Optional

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "dados.db")

# Conexão única com check_same_thread=False para uso por threads + Mutex
_conn: Optional[sqlite3.Connection] = None
_lock = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def init_db():
    conn = _get_conn()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                ts      INTEGER NOT NULL,
                node_id TEXT    NOT NULL,
                room_id TEXT    NOT NULL,
                temp    REAL,
                rh      REAL,
                pm25    REAL,
                mode    TEXT,
                PRIMARY KEY (ts, node_id)
            )
        """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS ix_room_ts ON readings(room_id, ts)")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_node_ts ON readings(node_id, ts)")


def insert_reading(
    ts: int,
    node_id: str,
    room_id: str,
    temp: Any = None,
    rh: Any = None,
    pm25: Any = None,
    mode: Any = None,
):
    conn = _get_conn()
    with _lock:  # evita concorrência de múltiplas threads
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO readings (ts, node_id, room_id, temp, rh, pm25, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (ts, node_id, room_id, temp, rh, pm25, mode),
            )

def delete_all():
    """Apaga todas as leituras (para testes)."""
    conn = _get_conn()
    with _lock:
        with conn:
            conn.execute("DELETE FROM readings")
            conn.commit()
            
def get_last_readings(limit: int = 50, room_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor()
    if room_id:
        cur.execute(
            """
            SELECT ts, room_id, temp, rh
            FROM readings
            WHERE room_id = ?
            ORDER BY ts DESC
            LIMIT ?
        """,
            (room_id, limit),
        )
    else:
        cur.execute(
            """
            SELECT ts, room_id, temp, rh
            FROM readings
            ORDER BY ts DESC
            LIMIT ?
        """,
            (limit,),
        )
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_latest_by_room() -> Dict[str, Dict[str, Any]]:
    """
    Retorna um dicionário: { room_id: última_linha }
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.*
        FROM readings r
        JOIN (
            SELECT room_id, MAX(ts) AS max_ts
            FROM readings
            GROUP BY room_id
        ) x
          ON r.room_id = x.room_id AND r.ts = x.max_ts
        ORDER BY r.room_id
    """
    )
    rows = cur.fetchall()
    return {row["room_id"]: dict(row) for row in rows}


def count_rows() -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM readings")
    return int(cur.fetchone()[0])

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

def migrate_db():
    """
    Garante que a tabela 'readings' tenha as colunas/índices esperados:
    - coluna packet_number
    - índice ix_packet_number_ts(packet_number, ts)
    - (opcional) copiar room_id -> packet_number se existir coluna antiga
    """
    conn = _get_conn()
    cur = conn.cursor()

    # Descobrir colunas atuais
    cur.execute("PRAGMA table_info(readings)")
    cols = [row[1] for row in cur.fetchall()]

    # 1) Adicionar coluna packet_number, se ainda não existir
    if "packet_number" not in cols:
        cur.execute("ALTER TABLE readings ADD COLUMN packet_number TEXT")

        # Se existia room_id na versão antiga, podemos copiar os valores.
        if "room_id" in cols:
            cur.execute(
                "UPDATE readings SET packet_number = room_id WHERE packet_number IS NULL"
            )

    # 2) Criar índice em packet_number + ts (só funciona se coluna existir)
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_packet_number_ts
        ON readings(packet_number, ts)
        """
    )

    conn.commit()



def init_db():
    conn = _get_conn()
    with conn:
        # Cria tabela básica se não existir (sem assumir colunas novas)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                ts   INTEGER NOT NULL,
                temp REAL,
                rh   REAL
            )
        """
        )


def insert_reading(
    ts: int,
    packet_number: str,
    temp: Any = None,
    rh: Any = None,
):
    conn = _get_conn()
    with _lock:  # evita concorrência de múltiplas threads
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO readings (ts, packet_number, temp, rh)
                VALUES (?, ?, ?, ?)
            """,
                (ts, packet_number, temp, rh),
            )

def delete_all():
    """Apaga todas as leituras (para testes)."""
    conn = _get_conn()
    with _lock:
        with conn:
            conn.execute("DELETE FROM readings")
            conn.commit()
            
def get_last_readings(limit: int = 50, packet_number: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = _get_conn()
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
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def get_latest_by_packet() -> Dict[str, Dict[str, Any]]:
    """
    Retorna um dicionário: { packet_number: última_linha }
    """
    conn = _get_conn()
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
    rows = cur.fetchall()
    return {row["packet_number"]: dict(row) for row in rows}

def get_last_readings_for_packet(packet_number: str, limit: int = 20):
    conn = _get_conn()
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
    return [dict(r) for r in rows][::-1]  # inverte para ordem cronológica

def count_rows() -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM readings")
    return int(cur.fetchone()[0])

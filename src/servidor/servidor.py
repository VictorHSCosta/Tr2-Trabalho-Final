#!/usr/bin/env python3
"""
Servidor HTTP.
- POST /ingest  : recebe leituras em JSON e enfileira para persistência
- GET  /dashboard : renderiza HTML simples com últimas leituras
- GET  /health : status rápido

Execução:
  python3 servidor.py
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
import time
import logging
import threading
import queue
import os
from typing import Any, Dict

# Módulos locais
import storage
import dashboard

HOST = os.environ.get("LORA_HOST", "0.0.0.0")
PORT = int(os.environ.get("LORA_PORT", "8080"))

# Fila de ingestão (producer: handler; consumer: worker de persistência)
INGEST_QUEUE: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=10_000)

# ---------- Logging básico ----------
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(threadName)s - %(message)s",
)
log = logging.getLogger("lora-server")

# ---------- Worker de persistência ----------
def worker_persistencia():
    log.info("Worker de persistência iniciado.")
    while True:
        item = INGEST_QUEUE.get()
        if item is None:  # sinal de parada (não usado em execução normal)
            break
        try:
            storage.insert_reading(
                ts=item["ts"],
                node_id=item["node_id"],
                room_id=item.get("room_id", "DEFAULT"),
                temp=item.get("t"),
                rh=item.get("rh"),
                pm25=item.get("pm25"),
                mode=item.get("mode"),
            )
        except Exception as e:
            log.exception("Falha ao persistir leitura: %s", e)
        finally:
            INGEST_QUEUE.task_done()


persist_thread = threading.Thread(target=worker_persistencia, name="persist", daemon=True)
persist_thread.start()


# ---------- HTTP Handler ----------
class Handler(BaseHTTPRequestHandler):
    server_version = "LoRaProto/1.0"

    def _send(self, code: int, content: bytes, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/dashboard"):
            qs = parse_qs(parsed.query)
            room_id = qs.get("room_id", [None])[0]

            # Dados para o dashboard
            last_by_room = storage.get_latest_by_room()
            recent = storage.get_last_readings(limit=50, room_id=room_id)

            stats = {
                "queued": INGEST_QUEUE.qsize(),
                "rooms": len(last_by_room),
                "total_rows": storage.count_rows(),
                "updated_at": time.time(),
                "filtered_room": room_id,
            }
            html = dashboard.render_html(last_by_room=last_by_room, recent=recent, stats=stats)
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return

        if parsed.path == "/health":
            payload = {"ok": True, "queue": INGEST_QUEUE.qsize(), "time": int(time.time())}
            self._send(200, json.dumps(payload).encode("utf-8"), "application/json")
            return

        if parsed.path == "/api/last":
            # Endpoint simples para debug/validação automática
            data = storage.get_latest_by_room()
            self._send(200, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json")
            return

        self._send(404, b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/ingest":
            self._send(404, b"Not Found")
            return

        # Lê payload
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            log.warning("Payload inválido: %s", e)
            self._send(400, b"Bad Request: invalid JSON")
            return

        # Validação mínima
        required = ("node_id",)
        if not all(k in data for k in required):
            self._send(422, b"Unprocessable Entity: missing node_id")
            return

        # Campos padrão
        data.setdefault("ts", int(time.time()))
        data.setdefault("room_id", "DEFAULT")
        # Bons nomes curtos (opcionais) já previstos: t (temp), rh, pm25, mode

        # Enfileira para persistência
        try:
            INGEST_QUEUE.put_nowait(data)
        except queue.Full:
            log.error("Fila cheia! descartando leitura.")
            self._send(503, b"Service Unavailable: queue full")
            return

        # 202 para indicar que foi aceito e será processado
        self._send(202, b"Accepted")

    # Silencia log de cada GET no console (opcional)
    def log_message(self, fmt, *args):
        log.info("%s - %s", self.address_string(), fmt % args)


def main():
    storage.init_db()  # garante esquema pronto
    with ThreadingHTTPServer((HOST, PORT), Handler) as httpd:
        log.info("Servidor escutando em http://%s:%d", HOST, PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log.info("Encerrando servidor...")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simulador simples de um nó sensor LoRa (Entrega 1 - Protótipo Lógico)
Gera dados falsos e envia periodicamente via HTTP POST /ingest.

Uso:
    python3 simulador.py
"""

import json
import time
import random
import urllib.request

SERVER_URL = "http://localhost:8080/ingest"  # URL do servidor
NODE_ID = "N01"
ROOM_ID = "RACK_A"
INTERVAL = 5  # segundos entre envios

def gerar_leitura():
    """Gera uma leitura aleatória simples."""
    return {
        "ts": int(time.time()),
        "node_id": NODE_ID,
        "room_id": ROOM_ID,
        "t": round(random.uniform(22.0, 28.0), 1),   # temperatura °C
        "rh": round(random.uniform(40.0, 70.0), 1),  # umidade %
        "pm25": round(random.uniform(10.0, 50.0), 1),# poeira µg/m³
        "mode": "fixed"
    }

def enviar_dado(dado):
    """Envia o dado ao servidor via HTTP POST."""
    try:
        body = json.dumps(dado).encode("utf-8")
        req = urllib.request.Request(SERVER_URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[{time.strftime('%H:%M:%S')}] Enviado -> {resp.status} {resp.reason}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar: {e}")

def main():
    print("=== Simulador de Nó LoRa (protótipo lógico) ===")
    print(f"Enviando dados para: {SERVER_URL}")
    print("Pressione Ctrl+C para parar.\n")

    try:
        while True:
            dado = gerar_leitura()
            enviar_dado(dado)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nSimulador encerrado.")

if __name__ == "__main__":
    main()

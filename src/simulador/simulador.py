import serial
import time
import json
import time
import urllib.request

SERVER_URL = "http://localhost:8080/ingest"  # URL do servidor
INTERVAL = 5  # segundos entre envios
PORTA = '/dev/ttyACM0'
BAUD_RATE = 115200

def main():
    print("=== Leitor Serial Python ===")
    ser = serial.Serial(PORTA, BAUD_RATE, timeout=1)
    time.sleep(2)  # Aguarda 2 segundos para estabilizar
    print(f"Conectado com sucesso em {PORTA}")
    print(f"Aguardando dados do ESP32S3...\n")
    print("="*50)
    # Loop infinito para ler os dados
    while True:
        if ser.in_waiting > 0:  # Se há dados disponíveis
            # Lê uma linha da serial
            linha = ser.readline().decode('utf-8').strip()
            if linha:  # Se a linha não está vazia
                dados_serial = paserver(linha)
                # print(f"Temperatura: {dados_serial[0]} °C, Umidade: {dados_serial[1]} %")
                dados_dashboard = gerar_leitura(dados_serial[0], dados_serial[1])
                enviar_dado(dados_dashboard)
                time.sleep(INTERVAL)

def paserver(linha: str) -> list[float]:
    temperatura, umidade = list(map(float, linha.split(",")))  # temperatura, umidade
    return [temperatura, umidade]

def gerar_leitura(temperatura: float, umidade: float) -> dict:
    """Gera uma leitura aleatória simples."""
    return {
        "ts": int(time.time()),
        "t": temperatura,   # temperatura °C
        "rh": umidade,  # umidade %
        "mode": "fixed",
        "node_id": 17
    }

def enviar_dado(dado: dict):
    """Envia o dado ao servidor via HTTP POST."""
    try:
        body = json.dumps(dado).encode("utf-8")
        req = urllib.request.Request(SERVER_URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[{time.strftime('%H:%M:%S')}] Enviado -> {resp.status} {resp.reason}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar: {e}")

if __name__ == "__main__":
    main()
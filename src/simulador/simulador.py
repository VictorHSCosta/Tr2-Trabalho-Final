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
    pacote_anterior = None
    print("=== Leitor Serial Python ===")
    ser = serial.Serial(PORTA, BAUD_RATE, timeout = 1)
    time.sleep(2)
    print(f"Conectado com sucesso em {PORTA}")
    print(f"Aguardando dados do ESP32S3...\n")
    print("="*50)

    while True:
        if ser.in_waiting > 0:  # Se há dados disponíveis
            # Lê uma linha da serial
            linha = ser.readline().decode('utf-8').strip()
            # Se a linha for inválida
            if not linha:
                continue
            # Se a linha não está vazia
            if linha:
                dados_serial = paserver(linha)
                # Verifico o número do pacote recebido pela porta serial
                numero_do_pacote_atual = dados_serial[0]
                # Caso o pacote seja duplicado
                if numero_do_pacote_atual == pacote_anterior:
                    continue
                # Caso seja um pacote novo
                pacote_anterior = numero_do_pacote_atual
                print(f"Número do pacote: {dados_serial[0]}, Temperatura: {dados_serial[1]}°C, Umidade {dados_serial[2]} %")

def paserver(linha: str) -> list:
    numero_do_pacote, temperatura, umidade = linha.split(",")
    return [int(numero_do_pacote), float(temperatura), float(umidade)]

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
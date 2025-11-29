import serial
import time
import json
import time
import urllib.request

SERVER_URL = "http://localhost:8080/ingest"  # URL do servidor
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
                numero_do_pacote_atual, temperatura_atual, umidade_atual = paserver(linha)
                # Verifico o número do pacote recebido pela porta serial
                # Caso o pacote seja duplicado
                if numero_do_pacote_atual == pacote_anterior:
                    continue
                # Caso seja um pacote novo
                pacote_anterior = numero_do_pacote_atual
                print(f"Número do pacote: {numero_do_pacote_atual}, Temperatura: {temperatura_atual}°C, Umidade {umidade_atual} %")
                # Preparo o dado no formato esperado pelo servidor
                dados_dashboard = gerar_leitura(numero_do_pacote_atual, temperatura_atual, umidade_atual)
                # Envio o dado para o servidor
                enviar_dado(dados_dashboard)

def paserver(linha: str) -> list:
    numero_do_pacote, temperatura, umidade = linha.split(",")
    return [int(numero_do_pacote), float(temperatura), float(umidade)]

def gerar_leitura(numero_pacote: int, temperatura: float, umidade: float) -> dict:
    """Gera uma leitura para enviar ao servidor no formato JSON."""
    return {
        "ts": int(time.time()),
        "packet_number": numero_pacote,
        "t": temperatura,   # temperatura °C
        "rh": umidade,  # umidade %
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
#include "DHT.h"
#include <RadioLib.h>

#define DHTTYPE DHT11
#define DHTPIN 5 // Pino D4
#define tempoDeSono 5 * 1000000
#define variacaoMinDaTemperatura 0
#define variacaoMinDaUmidade 0

DHT dht(DHTPIN, DHTTYPE);

RTC_DATA_ATTR int contadorDePacotes = 0;
RTC_DATA_ATTR float ultimaTemperatura = -10.0;
RTC_DATA_ATTR float ultimaUmidade = -10.0;

SX1262 radio = new Module(41, 39, 42, 40);

void deepSleep();

void setup() {
  Serial.begin(115200);
  delay(1000);

  dht.begin();

  int state = radio.begin();
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println("Cliente iniciado com sucesso !");
  }
  else {
    Serial.print("Falhou ao iniciar rádio, código: ");
    Serial.println(state);
    deepSleep();
  }

  radio.setFrequency(915.0);
  radio.setOutputPower(22);
  radio.setSpreadingFactor(7);
  radio.setBandwidth(125.0);
  radio.setCodingRate(5);

  Serial.println("\n --- Ciclo de Leitura ---");

  float temperaturaAtual = dht.readTemperature();
  float umidadeAtual = dht.readHumidity();

  Serial.print("Leitura: ");
  Serial.print(temperaturaAtual);
  Serial.print("C | ");
  Serial.print(umidadeAtual);
  Serial.println("%");

  bool enviar = false;

  // 1) Caso seja a primeira leitura
  if (ultimaTemperatura == -10.0 && ultimaUmidade == -10) {
    enviar = true;
  }
  else {
    // 2) Calcula a variação da temperatura e caso seja maior que o estabelecido envio
    float variacaoDaTemperatura = abs(temperaturaAtual - ultimaTemperatura);
    float variacaoDaUmidade = abs(umidadeAtual - ultimaUmidade);

    if (variacaoDaTemperatura >= variacaoMinDaTemperatura || variacaoDaUmidade >= variacaoMinDaUmidade) {
      enviar = true;
      }
    }

  if (enviar) {
    contadorDePacotes++;
    String mensagem = String(contadorDePacotes) + "," + String(temperaturaAtual, 1) + "," + String(umidadeAtual, 1);

    int stateTransmit = radio.transmit(mensagem);

    Serial.println(mensagem);

    if (stateTransmit == RADIOLIB_ERR_NONE) {
      ultimaTemperatura = temperaturaAtual;
      ultimaUmidade = umidadeAtual;
    }
    else {
      Serial.print("Erro no envio: ");
      Serial.println(stateTransmit);
    }
  }

  deepSleep();
}

void loop() {

}

void deepSleep() {
  radio.sleep();

  Serial.println("Indo dormir...");
  Serial.flush();

  esp_sleep_enable_timer_wakeup(tempoDeSono);

  esp_deep_sleep_start();
}
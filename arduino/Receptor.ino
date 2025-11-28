#include <RadioLib.h>

SX1262 radio = new Module(41, 39, 42, 40);

void setup() {
  Serial.begin(115200);
  delay(1000);
  int state = radio.begin();

  if (state == RADIOLIB_ERR_NONE) {
    //Serial.println("Envio recebido.\n");
  } else {
    //Serial.print("Falhou, código: ");
    Serial.println(state);
    while (true);
  }
  radio.setFrequency(915.0);
  radio.setSpreadingFactor(7);
  radio.setBandwidth(125.0);
  radio.setCodingRate(5);
  radio.startReceive();
}

void loop() {
  String mensagem;
  int state = radio.readData(mensagem);

  if (state == RADIOLIB_ERR_NONE) {
    //Serial.print("Recebido: ");
    Serial.println(mensagem);
    //Serial.println("---------------------------");
  }
  else if (state == RADIOLIB_ERR_RX_TIMEOUT) {
  }
  else {
    Serial.print("Erro de recepção: ");
    Serial.println(state);
  }
  delay(5000);
}
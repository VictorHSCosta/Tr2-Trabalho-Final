#include <RadioLib.h>

SX1262 radio = new Module(41, 39, 42, 40);

void setup() {
  Serial.begin(115200);
  delay(1000);
  int state = radio.begin();
  if (state == RADIOLIB_ERR_NONE) {
    //Serial.println("Sucesso!");
  } else {
    //Serial.print("Falhou, código: ");
    Serial.println(state);
    while (true);
  }
  radio.setFrequency(915.0);
  radio.setOutputPower(22);
  radio.setSpreadingFactor(7);
  radio.setBandwidth(125.0);
  radio.setCodingRate(5);  
}

void loop() {
  float temperatura = random(180, 300)/10.0;
  float umidade = random(400, 800)/10.0;

  String mensagem = String(temperatura, 1) + "," + String(umidade, 1) + "\n";
  Serial.print(mensagem);
  int state = radio.transmit(mensagem);
  
  if (state == RADIOLIB_ERR_NONE) {
  } else {
    Serial.print("\nFalhou, código: ");
    Serial.println(state);
  }
  
  delay(5000);
}
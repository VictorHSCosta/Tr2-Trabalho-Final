# 🌡️📡 Monitoramento de Condições Ambientais via LoRa

Projeto final da disciplina **Teleinformática e Redes 2 (CIC0236)**, envolvendo a criação de um sistema completo para monitoramento remoto de **temperatura** e **umidade** utilizando comunicação **LoRa** — ideal para longas distâncias e baixo consumo energético.

## 📋 Visão Geral

O sistema coleta dados ambientais por meio do sensor **DHT11**, transmite via rádio utilizando módulos **SX1262**, e disponibiliza todas as informações em um **dashboard web em tempo real**.

## 🛠️ Arquitetura e Tecnologias

### 📡 Cliente LoRa (Transmissor)
- ESP32-S3  
- Módulo LoRa **SX1262**  
- Sensor **DHT11**  
- Estratégias de economia de energia:  
  - **Deep Sleep**  
  - **Send-on-Delta** (envio apenas quando houver variação relevante)

### 🛜 Gateway
- ESP32-S3 + SX1262  
- Comunicação via **Serial** com script em **Python**

### 🖥️ Servidor & Dashboard
- Servidor **HTTP** em Python  
- Banco de dados **SQLite**  
- Dashboard web com **atualização automática**

## 👥 Autores
- Henrique Givisiez dos Santos  
- Gabriel Francisco de Oliveira Castro  
- Víctor Henrique da Silva Costa

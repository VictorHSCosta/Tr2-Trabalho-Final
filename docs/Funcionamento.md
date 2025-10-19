````markdown
# Sistema de Monitoramento via LoRa — Protótipo Lógico (Entrega 1)

## Visão geral
Este protótipo demonstra o fluxo completo de dados usando apenas a biblioteca padrão do Python:  
**simulador → servidor HTTP → banco SQLite → dashboard HTML**.  
Não há LoRa real nesta etapa; os dados são gerados artificialmente (pelo `simulador.py`).

---

## Componentes (`src/`)

### 1) `servidor/servidor.py`
- Sobe um **HTTP server** (`ThreadingHTTPServer`) na porta **8080**.  
- **Endpoints:**
  - `POST /ingest` : recebe leituras em JSON e coloca em uma fila (`queue`).
  - `GET /dashboard` : retorna uma página HTML com últimas leituras e métricas.
  - `GET /api/last` : retorna, em JSON, a última leitura por sala (debug).
  - `GET /health` : status simples do servidor.
- **Worker de persistência:**
  - Uma thread separada lê a fila e grava no banco via `storage.py`.
  - Resposta a `/ingest` é **202 Accepted** (processamento assíncrono).
- **Logging básico** configurado com níveis padrão.

---

### 2) `servidor/storage.py`
- Abstrai a persistência com **SQLite** (`database/dados.db`).
- Cria a tabela `readings` (`ts`, `node_id`, `room_id`, `temp`, `rh`, `pm25`, `mode`).
- **Funções principais:**
  - `init_db()` — garante o esquema e índices.
  - `insert_reading(...)` — insere/atualiza uma leitura.
  - `get_last_readings(...)` — últimas N leituras (geral ou por sala).
  - `get_latest_by_room()` — última leitura por sala (para os cards).
  - `count_rows()` — total de linhas (métricas).

---

### 3) `servidor/dashboard.py`
- Gera o **HTML simples do dashboard** (sem frameworks).
- Exibe “cards” com a última leitura por sala e uma tabela de leituras recentes.
- A página usa **meta refresh** (autoatualização a cada 5 s).

---

### 4) `simulador/simulador.py`
- Versão simplificada: gera periodicamente **leituras falsas** e envia via `HTTP POST /ingest`.
- **Campos enviados (JSON):**
  ```json
  {
    "ts":   <epoch em segundos>,
    "node_id": "N01",
    "room_id": "RACK_A",
    "t":    <temperatura °C>,
    "rh":   <umidade relativa %>,
    "pm25": <poeira µg/m³>,
    "mode": "fixed"
  }
````

---

## Fluxo de execução

1. **Inicie o servidor:**

   ```bash
   cd src/servidor
   python3 servidor.py
   ```

   → Disponível em [http://localhost:8080](http://localhost:8080)

2. **Em outro terminal, rode o simulador:**

   ```bash
   cd src/simulador
   python3 simulador.py
   ```

3. **Abra o dashboard no navegador:**

   * [http://localhost:8080/dashboard](http://localhost:8080/dashboard)
   * ou [http://localhost:8080/](http://localhost:8080/)

---

## Fluxo de dados em alto nível

```
simulador.py  --(HTTP POST /ingest)-->  servidor.py
servidor.py   --(queue)--> worker_persistencia --(SQLite)--> storage.py
dashboard.py  <--(consulta SQLite)--> servidor.py  ← (GET /dashboard) navegador
```

---

## Pastas relevantes

```
src/servidor   → código do servidor, dashboard e persistência
src/simulador  → código do gerador de dados falsos
database/      → arquivo SQLite (dados.db)
docs/          → diagramas, prints e relatório
```

---

## Observações

* O protótipo usa **apenas a biblioteca padrão do Python**:

  ```
  http.server, sqlite3, threading, queue, logging
  ```

```

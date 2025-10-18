"""
Gera HTML simples para o dashboard.
- render_html(last_by_room, recent, stats) -> str
"""

import time
from html import escape
from typing import Any, Dict, List


def _fmt_ts(ts: int) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts)))
    except Exception:
        return str(ts)


def render_html(
    last_by_room: Dict[str, Dict[str, Any]],
    recent: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> str:
    # Cards de última leitura por sala
    cards = []
    if not last_by_room:
        cards.append("<p><em>Sem dados ainda.</em></p>")
    else:
        for room_id, row in last_by_room.items():
            card = f"""
            <div class="card">
              <h3>Sala: {escape(str(room_id))}</h3>
              <p><strong>Timestamp:</strong> {_fmt_ts(row.get('ts'))}</p>
              <p><strong>Node:</strong> {escape(str(row.get('node_id')))}</p>
              <p><strong>Temp:</strong> {row.get('temp')} °C |
                 <strong>UR:</strong> {row.get('rh')} % |
                 <strong>PM2.5:</strong> {row.get('pm25')} µg/m³</p>
              <p><strong>Modo:</strong> {escape(str(row.get('mode')))}</p>
            </div>
            """
            cards.append(card)

    # Tabela de últimas leituras (recortes)
    rows_html = []
    for r in recent:
        rows_html.append(
            f"<tr>"
            f"<td>{_fmt_ts(r.get('ts'))}</td>"
            f"<td>{escape(str(r.get('room_id')))}</td>"
            f"<td>{escape(str(r.get('node_id')))}</td>"
            f"<td>{escape(str(r.get('temp')))}</td>"
            f"<td>{escape(str(r.get('rh')))}</td>"
            f"<td>{escape(str(r.get('pm25')))}</td>"
            f"<td>{escape(str(r.get('mode')))}</td>"
            f"</tr>"
        )

    filtered = f" (filtro: room_id={escape(stats['filtered_room'])})" if stats.get("filtered_room") else ""
    updated = _fmt_ts(int(stats.get("updated_at", time.time())))

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Dashboard LoRa - Protótipo</title>
  <meta http-equiv="refresh" content="5"> <!-- auto-refresh a cada 5s -->
  <style>
    body {{ font-family: system-ui, Arial, sans-serif; margin: 20px; }}
    header {{ display:flex; align-items:baseline; gap:12px; }}
    .metrics {{ margin: 10px 0 20px; color:#444; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 12px; background:#fafafa; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; font-size: 14px; }}
    th {{ background: #f0f0f0; }}
    .muted {{ color:#666; font-size: 13px; }}
    .footer {{ margin-top: 24px; color:#666; font-size: 12px; }}
    code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
    .pill {{ display:inline-block; background:#eef; border:1px solid #ccd; padding:2px 6px; border-radius:999px; font-size:12px; margin-right:6px; }}
  </style>
</head>
<body>
  <header>
    <h1>Dashboard – Sistema de Monitoramento (Protótipo)</h1>
    <span class="pill">Salas: {stats.get('rooms', 0)}</span>
    <span class="pill">Leituras: {stats.get('total_rows', 0)}</span>
    <span class="pill">Fila: {stats.get('queued', 0)}</span>
  </header>

  <div class="metrics">
    <div>Última atualização: <strong>{updated}</strong>{filtered}</div>
    <div class="muted">Use <code>/dashboard?room_id=RACK_A</code> para filtrar por sala.</div>
    <div class="muted">API de debug: <code>/api/last</code> | Saúde: <code>/health</code></div>
  </div>

  <h2>Última leitura por sala</h2>
  <div class="grid">
    {''.join(cards)}
  </div>

  <h2>Leituras recentes</h2>
  <table>
    <thead>
      <tr>
        <th>Timestamp</th>
        <th>Sala</th>
        <th>Nó</th>
        <th>Temp (°C)</th>
        <th>UR (%)</th>
        <th>PM2.5 (µg/m³)</th>
        <th>Modo</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html) or '<tr><td colspan="7"><em>Sem dados</em></td></tr>'}
    </tbody>
  </table>

  <div class="footer">
    <p class="muted">
      Protótipo lógico (Entrega 1) — stdlib Python: http.server, sqlite3.
      Próximo passo: payload compacto binário + gateway LoRa real.
    </p>
  </div>
</body>
</html>
"""
    return html

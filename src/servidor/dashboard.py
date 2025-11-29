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
    last_packet: Dict[str, Dict[str, Any]],
    recent: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> str:
    # Cards de última leitura por sala
    cards = []
    if not last_packet:
        cards.append("<div class='card empty'><em>Sem dados ainda.</em></div>")
    else:
        for packet_number, row in last_packet.items():
            ts = _fmt_ts(row.get("ts"))
            temp = escape(str(row.get("temp", "—")))
            rh = escape(str(row.get("rh", "—")))
            card = f"""
            <div class="card">
              <div class="card-head">
                <h3 class="room">N° Pacote {escape(str(packet_number))}</h3>
                <div class="small muted">{ts}</div>
              </div>
              <div class="card-body">
                <div class="stat">
                  <div class="label">🌡️ Temperatura</div>
                  <div class="value">{temp} °C</div>
                </div>
                <div class="stat">
                  <div class="label">💧 UR</div>
                  <div class="value">{rh} %</div>
                </div>
              </div>
            </div>
            """
            cards.append(card)

    # Tabela de últimas leituras (recortes)
    rows_html = []
    for r in recent:
        rows_html.append(
            "<tr>"
            f"<td>{_fmt_ts(r.get('ts'))}</td>"
            f"<td>{escape(str(r.get('packet_number')))}</td>"
            f"<td>{escape(str(r.get('temp')))}</td>"
            f"<td>{escape(str(r.get('rh')))}</td>"
            "</tr>"
        )

    # Compatível com stats['filtered_packet'] ou stats['filtered_room']
    filtered_value = stats.get("filtered_packet") or stats.get("filtered_room")
    filtered = (
        f" (filtro: packet_number={escape(str(filtered_value))})"
        if filtered_value
        else ""
    )
    updated = _fmt_ts(int(stats.get("updated_at", time.time())))

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Dashboard LoRa - Protótipo</title>
  <meta http-equiv="refresh" content="5"> <!-- auto-refresh a cada 5s -->
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    :root {{
      --bg: #fbfdff;
      --card: #ffffff;
      --muted: #68707a;
      --accent: #2b6cb0;
      --border: #e6eef8;
      --shadow: 0 6px 18px rgba(32,40,55,0.06);
      --radius: 10px;
      --danger: #e53e3e;
      --danger-soft: #fff5f5;
      --danger-border: #fed7d7;
    }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin: 20px; background: var(--bg); color:#0b1220; }}
    header {{ display:flex; flex-wrap:wrap; align-items:baseline; gap:12px; justify-content:space-between; }}
    header h1 {{ margin:0; font-size:20px; letter-spacing: -0.2px; }}
    .sub {{ color:var(--muted); font-size:13px; }}
    .topline {{ display:flex; gap:8px; align-items:center; }}
    .pill {{ display:inline-block; background: #eef6ff; border:1px solid var(--border); padding:6px 10px; border-radius:999px; font-size:13px; color:var(--accent); }}
    .metrics {{ margin: 8px 0 18px; color:var(--muted); font-size:13px; }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding:12px; box-shadow: var(--shadow); }}
    .card.empty {{ text-align:center; color:var(--muted); padding:18px; }}
    .card-head {{ display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px; }}
    .room {{ margin:0; font-size:15px; }}
    .muted {{ color:var(--muted); font-size:12px; }}

    .card-body {{ display:flex; gap:12px; }}
    .stat {{ flex:1; padding:8px; background: linear-gradient(180deg,#fbfdff,#f6f9ff); border-radius:8px; border:1px solid #f0f6ff; text-align:center; }}
    .label {{ font-size:12px; color:var(--muted); }}
    .value {{ font-weight:600; margin-top:6px; font-size:15px; }}

    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; background: #fff; border-radius:8px; overflow:hidden; box-shadow: var(--shadow); }}
    thead th {{ background: #f7fbff; padding:10px 12px; text-align:left; font-size:13px; color:var(--muted); border-bottom:1px solid var(--border); }}
    tbody td {{ padding:10px 12px; font-size:14px; border-bottom:1px solid #f1f5f9; }}
    tbody tr:last-child td {{ border-bottom: none; }}

    @media (max-width:700px) {{
      header {{ gap:8px; flex-direction:column; align-items:flex-start; }}
      .topline {{ width:100%; justify-content:space-between; }}
      .card-body {{ flex-direction:column; }}
      thead th, tbody td {{ font-size:13px; padding:8px; }}
    }}

    .footer {{ margin-top: 18px; color:var(--muted); font-size:12px; }}
    code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size:13px; }}

    .btn-danger {{
      border-radius: 999px;
      border: 1px solid var(--danger-border);
      background: var(--danger-soft);
      color: var(--danger);
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display:inline-flex;
      align-items:center;
      gap:6px;
    }}
    .btn-danger:hover {{
      background: #fed7d7;
    }}
    .btn-danger span.icon {{
      font-size: 14px;
      line-height: 1;
    }}
    .danger-zone {{
      display:flex;
      align-items:center;
      gap:8px;
    }}
  </style>
  <script>
    function confirmDeleteAll(form) {{
      if (confirm("Tem certeza que deseja apagar TODAS as leituras do banco de dados?")) {{
        return true;
      }}
      return false;
    }}
  </script>
</head>
<body>
  <header>
    <div>
      <h1>Dashboard – Sistema de Monitoramento</h1>
      <div class="sub">Visão rápida</div>
    </div>
    <div class="topline">
      <span class="pill">Leituras: {stats.get('total_rows', 0)}</span>
      <div class="sub">Última: <strong>{updated}</strong>{filtered}</div>
      <form class="danger-zone" method="POST" action="/delete-all" onsubmit="return confirmDeleteAll(this);">
        <button type="submit" class="btn-danger" title="Apagar todos os dados do banco">
          <span class="icon">🗑️</span>
          <span>Apagar todos os dados</span>
        </button>
      </form>
    </div>
  </header>

  <h2 style="margin-top:18px;font-size:16px;">Última leitura</h2>
  <div class="grid" role="list">
    {''.join(cards)}
  </div>

  <h2 style="margin-top:18px;font-size:16px;">Leituras recentes</h2>
  <div style="overflow:auto;">
    <table role="table">
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Número do Pacote</th>
          <th>Temp (°C)</th>
          <th>UR (%)</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html) or '<tr><td colspan="4" style="padding:12px;"><em>Sem dados</em></td></tr>'}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Atualizado em <code>{updated}</code>. Página atualiza automaticamente a cada 5s.
  </div>
</body>
</html>
"""
    return html

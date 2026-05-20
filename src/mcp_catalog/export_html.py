"""Single-file HTML report (open locally without a server)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_standalone_html(path: Path, payload: dict[str, Any]) -> None:
    """Embed catalog JSON and render a dark, sortable table via vanilla JS."""
    data_json = json.dumps(payload, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>iflow-mcp-catalog — {payload.get("meta", {}).get("org", "org")}</title>
  <style>
    :root {{
      --bg: hsl(220 16% 8%);
      --panel: hsl(220 14% 12% / 0.85);
      --text: hsl(210 20% 92%);
      --muted: hsl(215 12% 60%);
      --accent: hsl(200 85% 55%);
      --border: hsl(220 12% 22%);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: system-ui, Segoe UI, Roboto, sans-serif;
      background: var(--bg); color: var(--text);
      min-height: 100vh;
    }}
    header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border);
      backdrop-filter: blur(12px);
      background: var(--panel);
      position: sticky; top: 0; z-index: 10;
    }}
    h1 {{ margin: 0; font-size: 1.15rem; font-weight: 600; }}
    .sub {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.35rem; }}
    .toolbar {{
      display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
      padding: 1rem 1.5rem;
    }}
    input, select {{
      background: hsl(220 14% 16%); color: var(--text);
      border: 1px solid var(--border); border-radius: 8px;
      padding: 0.45rem 0.65rem; font-size: 0.9rem;
    }}
    main {{ padding: 0 1.5rem 2rem; }}
    table {{
      width: 100%; border-collapse: collapse; font-size: 0.88rem;
      backdrop-filter: blur(8px);
      background: var(--panel); border-radius: 12px; overflow: hidden;
      border: 1px solid var(--border);
    }}
    th, td {{ padding: 0.55rem 0.65rem; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ cursor: pointer; user-select: none; color: var(--muted); font-weight: 600; }}
    th:hover {{ color: var(--accent); }}
    tr:hover td {{ background: hsl(220 14% 14% / 0.5); }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .pill {{
      display: inline-block; padding: 0.15rem 0.45rem; border-radius: 999px;
      font-size: 0.75rem; background: hsl(220 14% 20%); border: 1px solid var(--border);
    }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body>
  <header>
    <h1>iflow-mcp-catalog</h1>
    <div class="sub" id="meta"></div>
  </header>
  <div class="toolbar">
    <label>Search <input type="search" id="q" placeholder="name / description" /></label>
    <label>Category <select id="cat"><option value="">all</option></select></label>
    <label>MCP score ≥ <input type="number" id="minscore" value="0" min="0" max="100" style="width:5rem"/></label>
  </div>
  <main>
    <table>
      <thead>
        <tr>
          <th data-k="stars">★ stars</th>
          <th data-k="name">repo</th>
          <th data-k="category">category</th>
          <th data-k="mcp_likelihood">mcp</th>
          <th data-k="language">lang</th>
          <th data-k="fork">fork</th>
          <th data-k="pushed_at">pushed</th>
        </tr>
      </thead>
      <tbody id="tb"></tbody>
    </table>
  </main>
  <script type="application/json" id="payload">{data_json}</script>
  <script>
    const payload = JSON.parse(document.getElementById('payload').textContent);
    const repos = payload.repos || [];
    const meta = payload.meta || {{}};
    document.getElementById('meta').textContent =
      `org=${{meta.org}} · repos=${{meta.repo_count}} · fetched=${{meta.fetched_at || '?'}}` +
      (meta.github_rate_limit_remaining != null
        ? ` · GH rate remaining=${{meta.github_rate_limit_remaining}}` : '');

    const cats = [...new Set(repos.map(r => r.category))].sort();
    const sel = document.getElementById('cat');
    for (const c of cats) {{
      const o = document.createElement('option');
      o.value = c; o.textContent = c;
      sel.appendChild(o);
    }}

    let sortKey = 'stars';
    let sortDir = -1;

    function rowMatches(r) {{
      const q = document.getElementById('q').value.toLowerCase();
      const cat = document.getElementById('cat').value;
      const minS = Number(document.getElementById('minscore').value) || 0;
      if (cat && r.category !== cat) return false;
      if ((r.mcp_likelihood || 0) < minS) return false;
      if (!q) return true;
      const blob = `${{r.full_name}} ${{r.description || ''}} ${{ (r.topics||[]).join(' ') }}`.toLowerCase();
      return blob.includes(q);
    }}

    function cmp(a, b, k) {{
      let va = a[k], vb = b[k];
      if (k === 'stars' || k === 'mcp_likelihood' || k === 'forks_count') {{
        va = Number(va) || 0; vb = Number(vb) || 0;
        return va === vb ? (a.full_name||'').localeCompare(b.full_name||'') : (va < vb ? -1 : 1);
      }}
      if (k === 'fork') {{
        va = va ? 1 : 0; vb = vb ? 1 : 0;
        return va - vb;
      }}
      va = (va ?? '').toString(); vb = (vb ?? '').toString();
      return va.localeCompare(vb);
    }}

    function render() {{
      let list = repos.filter(rowMatches);
      list = [...list].sort((a,b) => {{
        const c = cmp(a, b, sortKey);
        return c * sortDir;
      }});
      const tb = document.getElementById('tb');
      tb.innerHTML = '';
      for (const r of list) {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="num">${{r.stars}}</td>
          <td><a href="${{r.html_url}}" target="_blank" rel="noopener">${{r.full_name}}</a>
            ${{r.parent_full_name ? `<div class="sub" style="color:var(--muted);font-size:0.8rem">fork of ${{r.parent_full_name}}</div>` : ''}}</td>
          <td><span class="pill">${{r.category}}</span></td>
          <td class="num">${{r.mcp_likelihood}}</td>
          <td>${{r.language || '—'}}</td>
          <td>${{r.fork ? 'yes' : ''}}</td>
          <td>${{(r.pushed_at || '').slice(0,10)}}</td>`;
        tb.appendChild(tr);
      }}
    }}

    document.querySelectorAll('th[data-k]').forEach(th => {{
      th.addEventListener('click', () => {{
        const k = th.getAttribute('data-k');
        if (sortKey === k) sortDir *= -1;
        else {{ sortKey = k; sortDir = (k === 'name' || k === 'category' || k === 'language' || k === 'pushed_at') ? 1 : -1; }}
        render();
      }});
    }});
    ['q','cat','minscore'].forEach(id => document.getElementById(id).addEventListener('input', render));
    render();
  </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")

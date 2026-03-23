# iflow-mcp-catalog

**Repo:** [github.com/sandraschi/iflow-mcp-catalog](https://github.com/sandraschi/iflow-mcp-catalog)

FastMCP **3.1+** server plus SOTA webapp: pulls a GitHub org’s repos (default [`iflow-mcp`](https://github.com/iflow-mcp)), classifies them for MCP-oriented browsing, sorts by stars, and stores **`data/catalog.json`** plus optional **`reports/catalog_standalone.html`**.

## Ports (fleet)

| Role     | Port  |
|----------|-------|
| Vite UI  | 10808 |
| FastAPI  | 10809 |
| MCP HTTP | 10910 (optional; `MCP_TRANSPORT=http`) |

Registered in `mcp-central-docs`: `operations/WEBAPP_PORTS.md` and `operations/webapp-registry.json`.

## Setup (Windows)

```text
cd D:\Dev\repos\iflow-mcp-catalog
py -3.12 -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
cd webapp
npm install
```

## Refresh catalog (GitHub API)

Set a token for large orgs (public read is enough):

```text
$env:GITHUB_TOKEN = "ghp_..."
.\.venv\Scripts\iflow-mcp-catalog refresh
```

Test with a page cap:

```text
.\.venv\Scripts\iflow-mcp-catalog refresh --max-pages 1
```

## Web dashboard

```text
.\start.ps1
```

Opens `http://127.0.0.1:10808/` (Vite proxies `/api` → `10809`). If `catalog.json` is missing, the UI tells you to run `refresh`.

**Single-file report** (no server): open `reports/catalog_standalone.html` after a refresh with HTML enabled.

## MCP (stdio)

```text
.\.venv\Scripts\iflow-mcp-catalog mcp
```

Tools: `iflow_catalog_refresh`, `iflow_catalog_snapshot`, `iflow_catalog_paths`.

## Production-style (API + built SPA on one port)

```text
cd webapp
npm run build
cd ..
.\.venv\Scripts\iflow-mcp-catalog web --port 10809
```

Then open `http://127.0.0.1:10809/` (static from `webapp/dist` when present).

## Fleet architecture note

This repo is an **optional index satellite** for research/demos. How it plugs into RoboFang **without** duplicating server code into `robofang/tools/`: see **`mcp-central-docs/operations/FLEET_CONTROL_PLANE.md`**.

## Limits

- Classification is **heuristic** (name/topics/description), not ML.
- GitHub may omit `parent` on some list payloads; fork source can be null until GitHub fills it.

## License

MIT — see [LICENSE](LICENSE).

## Remote

```text
git remote add origin https://github.com/sandraschi/iflow-mcp-catalog.git
git push -u origin main
```

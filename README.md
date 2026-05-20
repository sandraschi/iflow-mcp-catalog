# iflow-mcp-catalog

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

**Repo:** [github.com/sandraschi/iflow-mcp-catalog](https://github.com/sandraschi/iflow-mcp-catalog)

FastMCP **3.1+** server plus SOTA webapp: pulls a GitHub orgs repos (default [`iflow-mcp`](https://github.com/iflow-mcp)), classifies them for MCP-oriented browsing, sorts by stars, and stores **`data/catalog.json`** plus optional **`reports/catalog_standalone.html`**.

## Ports (fleet)

| Role     | Port  |
|----------|-------|
| Vite UI  | 10808 |
| FastAPI  | 10809 |
| MCP HTTP | 10910 (optional; `MCP_TRANSPORT=http`) |

Registered in `mcp-central-docs`: `operations/WEBAPP_PORTS.md` and `operations/webapp-registry.json`.

## Quick Start

```powershell
git clone https://github.com/sandraschi/iflow-mcp-catalog
cd iflow-mcp-catalog
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:


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

Opens `http://127.0.0.1:10808/` (Vite proxies `/api`  `10809`). If `catalog.json` is missing, the UI tells you to run `refresh`.

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


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License

MIT  see [LICENSE](LICENSE).

## Remote

```text
git remote add origin https://github.com/sandraschi/iflow-mcp-catalog.git
git push -u origin main
```

"""CLI: MCP server, one-shot refresh, FastAPI web backend."""

from __future__ import annotations

import logging
import os

import typer
import uvicorn

app = typer.Typer(name="iflow-mcp-catalog", add_completion=False)
logger = logging.getLogger(__name__)


@app.command("mcp")
def cmd_mcp() -> None:
    """Run FastMCP (stdio default, or HTTP via MCP_TRANSPORT / flags)."""
    from .server import mcp
    from .transport import run_server

    run_server(mcp, server_name="iflow-mcp-catalog")


@app.command("refresh")
def cmd_refresh(
    org: str = typer.Option("sandraschi", "--org", help="GitHub org or personal account login"),
    max_pages: int | None = typer.Option(
        None,
        "--max-pages",
        help="Stop after N API pages (testing)",
    ),
    no_html: bool = typer.Option(False, "--no-html", help="Skip standalone HTML export"),
) -> None:
    """Fetch GitHub org repos and write data/catalog.json."""
    import asyncio

    from .catalog_service import (
        build_catalog_payload,
        export_standalone_report,
        write_catalog_json,
    )
    from .collector.github_org import fetch_org_repos

    async def _run() -> None:
        raw, diag = await fetch_org_repos(org, max_pages=max_pages)
        typer.echo(f"account type: {diag.get('account_type', 'unknown')}")
        payload = build_catalog_payload(org, raw, diag)
        jp = write_catalog_json(payload)
        typer.echo(f"wrote {jp} ({payload['meta']['repo_count']} repos)")
        if not no_html:
            hp = export_standalone_report(payload)
            typer.echo(f"wrote {hp}")

    asyncio.run(_run())


@app.command("web")
def cmd_web(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(10809, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload"),
) -> None:
    """Run FastAPI backend (catalog API); use Vite on 10808 for dev UI."""
    os.environ.setdefault("WEB_BACKEND_PORT", str(port))
    uvicorn.run(
        "iflow_mcp_catalog.webapp_backend:app",
        host=host,
        port=port,
        reload=reload,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    app()


if __name__ == "__main__":
    main()

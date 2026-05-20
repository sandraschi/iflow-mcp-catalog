"""FastMCP 3.1 dual transport (stdio default, HTTP streamable optional)."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

ENV_TRANSPORT = "MCP_TRANSPORT"
ENV_HOST = "MCP_HOST"
ENV_PORT = "MCP_PORT"
ENV_PATH = "MCP_PATH"


def get_transport_config() -> dict[str, str | int]:
    return {
        "transport": os.getenv(ENV_TRANSPORT, "stdio").lower(),
        "host": os.getenv(ENV_HOST, "127.0.0.1"),
        "port": int(os.getenv(ENV_PORT, "10910")),
        "path": os.getenv(ENV_PATH, "/mcp"),
    }


def create_argument_parser(server_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"{server_name} (FastMCP 3.1)")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--stdio", action="store_true", help="STDIO (default)")
    g.add_argument("--http", action="store_true", help="HTTP streamable")
    g.add_argument("--sse", action="store_true", help="SSE (deprecated)")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--path", default=None)
    parser.add_argument("--debug", action="store_true")
    return parser


def resolve_transport(args: argparse.Namespace) -> str:
    if args.http:
        return "http"
    if args.sse:
        return "sse"
    if args.stdio:
        return "stdio"
    t = os.getenv(ENV_TRANSPORT, "stdio").lower()
    return t if t in ("stdio", "http", "sse") else "stdio"


def resolve_config(args: argparse.Namespace) -> dict[str, str | int]:
    env = get_transport_config()
    return {
        "transport": resolve_transport(args),
        "host": args.host if args.host is not None else env["host"],
        "port": args.port if args.port is not None else env["port"],
        "path": args.path if args.path is not None else env["path"],
    }


def run_server(mcp_app: object, server_name: str = "iflow-mcp-catalog") -> None:
    asyncio.run(run_server_async(mcp_app, server_name))


async def run_server_async(mcp_app: object, server_name: str) -> None:
    parser = create_argument_parser(server_name)
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = resolve_config(args)
    transport = cfg["transport"]
    logger.info("Starting %s transport=%s", server_name, transport)

    if transport == "stdio":
        await mcp_app.run_stdio_async()  # type: ignore[union-attr]
    elif transport == "http":
        await mcp_app.run_http_async(  # type: ignore[union-attr]
            host=str(cfg["host"]),
            port=int(cfg["port"]),
            path=str(cfg["path"]),
        )
    else:
        logger.warning("SSE deprecated; prefer HTTP")
        await mcp_app.run_sse_async(host=str(cfg["host"]), port=int(cfg["port"]))  # type: ignore[union-attr]

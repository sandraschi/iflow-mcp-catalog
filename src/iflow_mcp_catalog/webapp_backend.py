"""FastAPI backend: catalog API + optional static SPA (production)."""

from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from .paths import catalog_json_path, repo_root

app = FastAPI(title="iflow-mcp-catalog API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10808",
        "http://localhost:10808",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "iflow-mcp-catalog"}


@app.get("/api/catalog")
async def get_catalog() -> JSONResponse:
    p = catalog_json_path()
    if not p.is_file():
        raise HTTPException(
            status_code=404,
            detail="catalog.json missing — run iflow-mcp-catalog refresh or MCP iflow_catalog_refresh",
        )
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid catalog JSON: {e}") from e
    return JSONResponse(content=data)


@app.get("/api/summary")
async def summary() -> dict[str, object]:
    p = catalog_json_path()
    if not p.is_file():
        return {"present": False}
    data = json.loads(p.read_text(encoding="utf-8"))
    meta = data.get("meta") or {}
    repos = data.get("repos") or []
    cats: dict[str, int] = {}
    for r in repos:
        c = r.get("category") or "other"
        cats[c] = cats.get(c, 0) + 1
    return {"present": True, "meta": meta, "category_counts": cats, "repo_count": len(repos)}


_dist = repo_root() / "webapp" / "dist"
if _dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="spa")

"""Build normalized catalog document from raw GitHub repo dicts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from .classifier import classify_mcp_category, mcp_likelihood_score
from .export_html import write_standalone_html
from .paths import catalog_json_path, reports_dir


def _parent_full_name(raw: dict[str, Any]) -> str | None:
    parent = raw.get("parent")
    if isinstance(parent, dict):
        return parent.get("full_name")
    return None


def _license_spdx(raw: dict[str, Any]) -> str | None:
    lic = raw.get("license")
    if isinstance(lic, dict):
        return lic.get("spdx_id") or lic.get("key")
    return None


def normalize_repo(raw: dict[str, Any]) -> dict[str, Any]:
    name = raw.get("name") or ""
    desc = raw.get("description")
    topics = list(raw.get("topics") or [])
    cat = classify_mcp_category(name=name, description=desc, topics=topics)
    score = mcp_likelihood_score(name=name, description=desc, topics=topics)
    return {
        "full_name": raw.get("full_name"),
        "name": name,
        "html_url": raw.get("html_url"),
        "description": desc,
        "stars": raw.get("stargazers_count") or 0,
        "forks_count": raw.get("forks_count") or 0,
        "language": raw.get("language"),
        "fork": bool(raw.get("fork")),
        "archived": bool(raw.get("archived")),
        "disabled": bool(raw.get("disabled")),
        "pushed_at": raw.get("pushed_at"),
        "updated_at": raw.get("updated_at"),
        "created_at": raw.get("created_at"),
        "topics": topics,
        "category": cat,
        "mcp_likelihood": score,
        "parent_full_name": _parent_full_name(raw),
        "license_spdx": _license_spdx(raw),
        "default_branch": raw.get("default_branch"),
    }


def build_catalog_payload(
    org: str,
    raw_repos: list[dict[str, Any]],
    diag: dict[str, str | int | None],
) -> dict[str, Any]:
    normalized = [normalize_repo(r) for r in raw_repos]
    normalized.sort(key=lambda x: (-int(x["stars"]), x["full_name"] or ""))
    return {
        "meta": {
            "org": org,
            "fetched_at": datetime.now(UTC).isoformat(),
            "repo_count": len(normalized),
            "github_rate_limit_remaining": diag.get("rate_limit_remaining"),
            "pages_fetched": diag.get("pages_fetched"),
        },
        "repos": normalized,
        "by_category": _group_by_category(normalized),
    }


def _group_by_category(repos: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for r in repos:
        c = r.get("category") or "other"
        out.setdefault(c, []).append(r)
    for k in out:
        out[k].sort(key=lambda x: (-int(x["stars"]), x["full_name"] or ""))
    return out


def write_catalog_json(payload: dict[str, Any]) -> str:
    path = catalog_json_path()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def export_standalone_report(payload: dict[str, Any]) -> str:
    path = reports_dir() / "catalog_standalone.html"
    write_standalone_html(path, payload)
    return str(path)

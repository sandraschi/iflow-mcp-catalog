"""Paginated GitHub REST: list organization repositories."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def _parse_next_url(link_header: str | None) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        if 'rel="next"' in part:
            url = part.split(";")[0].strip()
            if url.startswith("<") and url.endswith(">"):
                return url[1:-1]
    return None


async def fetch_org_repos(
    org: str,
    *,
    token: str | None = None,
    per_page: int = 100,
    max_pages: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str | int | None]]:
    """
    Fetch all public repos for an org (including forks). Uses GitHub REST v3.

    Set GITHUB_TOKEN or pass token for higher rate limits (required for large orgs).
    """
    tok = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    repos: list[dict[str, Any]] = []
    # type=all includes public forks; sort=updated reduces stale tail when capped
    url = (
        f"https://api.github.com/orgs/{org}/repos"
        f"?per_page={per_page}&type=all&sort=updated&direction=desc"
    )
    pages = 0
    diag: dict[str, str | int | None] = {
        "rate_limit_remaining": None,
        "pages_fetched": 0,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        while url:
            if max_pages is not None and pages >= max_pages:
                logger.warning("Stopped at max_pages=%s (partial catalog)", max_pages)
                break
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            diag["rate_limit_remaining"] = resp.headers.get("x-ratelimit-remaining")
            batch = resp.json()
            if not isinstance(batch, list):
                raise RuntimeError(f"Unexpected GitHub API payload: {type(batch)}")
            repos.extend(batch)
            pages += 1
            diag["pages_fetched"] = pages
            url = _parse_next_url(resp.headers.get("link"))

    return repos, diag

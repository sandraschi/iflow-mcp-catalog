"""Paginated GitHub REST: list repositories for an org or personal account.

Auto-detects whether the target is a GitHub Organisation or a User account
and routes to the correct endpoint (/orgs/{org}/repos vs /users/{user}/repos).
"""

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


async def _resolve_account_type(
    client: httpx.AsyncClient,
    name: str,
    headers: dict[str, str],
) -> str:
    """Return 'Organization' or 'User' by probing /users/{name}."""
    resp = await client.get(
        f"https://api.github.com/users/{name}",
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json().get("type", "User")


async def fetch_org_repos(
    org: str,
    *,
    token: str | None = None,
    per_page: int = 100,
    max_pages: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str | int | None]]:
    """Fetch all public repos for a GitHub org or personal account.

    Auto-detects account type — pass either an org name (e.g. 'iflow-mcp')
    or a personal account name (e.g. 'sandraschi') and the right API endpoint
    is selected automatically.

    Set GITHUB_TOKEN or pass token for higher rate limits.
    """
    tok = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    repos: list[dict[str, Any]] = []
    pages = 0
    diag: dict[str, str | int | None] = {
        "rate_limit_remaining": None,
        "pages_fetched": 0,
        "account_type": None,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        account_type = await _resolve_account_type(client, org, headers)
        diag["account_type"] = account_type
        logger.info("Resolved '%s' as %s", org, account_type)

        if account_type == "Organization":
            base = (
                f"https://api.github.com/orgs/{org}/repos"
                f"?per_page={per_page}&type=all&sort=updated&direction=desc"
            )
        else:
            # User accounts: type=owner excludes repos the user merely has access to
            base = (
                f"https://api.github.com/users/{org}/repos"
                f"?per_page={per_page}&type=owner&sort=updated&direction=desc"
            )

        url: str | None = base
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

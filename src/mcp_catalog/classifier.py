"""Heuristic MCP category from name, topics, and description."""

from __future__ import annotations

_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "devtools",
        (
            "lsp",
            "vscode",
            "ide",
            "compiler",
            "debugger",
            "devtools",
            "github",
            "gitlab",
            "git-",
            "ast",
            "tree-sitter",
        ),
    ),
    (
        "media",
        (
            "video",
            "audio",
            "youtube",
            "image",
            "ffmpeg",
            "obs",
            "godot",
            "transcript",
            "subtitle",
        ),
    ),
    (
        "data",
        (
            "sql",
            "database",
            "postgres",
            "sqlite",
            "mongo",
            "redis",
            "csv",
            "warehouse",
            "snowflake",
            "bigquery",
        ),
    ),
    (
        "automation",
        (
            "playwright",
            "selenium",
            "browser",
            "scraping",
            "crawler",
            "rpa",
            "n8n",
            "zapier",
        ),
    ),
    (
        "infra",
        (
            "docker",
            "kubernetes",
            "k8s",
            "aws",
            "azure",
            "gcp",
            "terraform",
            "pulumi",
            "cloud",
        ),
    ),
    (
        "research",
        (
            "arxiv",
            "paper",
            "rag",
            "embedding",
            "vector",
            "llm",
            "openai",
            "anthropic",
        ),
    ),
    (
        "integrations",
        (
            "slack",
            "discord",
            "notion",
            "jira",
            "linear",
            "trello",
            "salesforce",
            "netsuite",
        ),
    ),
]


def classify_mcp_category(
    *,
    name: str,
    description: str | None,
    topics: list[str],
) -> str:
    """Return a coarse category bucket for dashboard grouping."""
    blob = f"{name} {' '.join(topics)} {description or ''}".lower()
    for cat, keywords in _RULES:
        if any(k in blob for k in keywords):
            return cat
    low = name.lower()
    if "mcp" in low or low.endswith("-mcp") or low.startswith("mcp-"):
        return "mcp-general"
    return "other"


def mcp_likelihood_score(
    *,
    name: str,
    description: str | None,
    topics: list[str],
) -> int:
    """0–100 rough score: how likely this repo is MCP-related."""
    score = 0
    low = name.lower()
    if "mcp" in low:
        score += 40
    if low.endswith("-mcp") or low.startswith("mcp-"):
        score += 20
    blob = f"{description or ''} {' '.join(topics)}".lower()
    for needle in (
        "model context protocol",
        "mcp server",
        "fastmcp",
        "claude",
        "anthropic",
    ):
        if needle in blob:
            score += 15
    if "mcp" in topics:
        score += 25
    return min(100, score)

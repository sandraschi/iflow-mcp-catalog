"""Unit tests for heuristic classifier."""

from iflow_mcp_catalog.classifier import classify_mcp_category, mcp_likelihood_score


def test_mcp_name_high_score() -> None:
    s = mcp_likelihood_score(name="foo-mcp", description=None, topics=[])
    assert s >= 40


def test_youtube_transcript_category() -> None:
    c = classify_mcp_category(
        name="youtube-transcript-mcp",
        description="MCP server for transcripts",
        topics=["youtube", "mcp"],
    )
    assert c == "media"


def test_default_other() -> None:
    c = classify_mcp_category(name="random-utils", description="helpers", topics=[])
    assert c == "other"

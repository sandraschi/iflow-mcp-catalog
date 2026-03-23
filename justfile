# Fleet-style tasks (optional; requires `just`)

default:
    @just --list

lint:
    uv run ruff check src tests
    uv run ruff format --check src tests

fmt:
    uv run ruff format src tests
    uv run ruff check --fix src tests

test:
    uv run pytest tests -q

refresh token:
    uv run iflow-mcp-catalog refresh

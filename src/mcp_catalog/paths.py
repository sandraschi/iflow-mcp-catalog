"""Repository root and data paths."""

from pathlib import Path


def repo_root() -> Path:
    """Project root (contains pyproject.toml, webapp/, data/)."""
    return Path(__file__).resolve().parent.parent.parent


def data_dir() -> Path:
    p = repo_root() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def catalog_json_path() -> Path:
    return data_dir() / "catalog.json"


def reports_dir() -> Path:
    p = repo_root() / "reports"
    p.mkdir(parents=True, exist_ok=True)
    return p

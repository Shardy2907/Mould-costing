"""Persists the last-used chart file path between runs."""

import json
from pathlib import Path

_CONFIG_DIR = Path.home() / ".mould_costing"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


def load_last_chart_path() -> str | None:
    if not _CONFIG_FILE.exists():
        return None
    try:
        data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        return data.get("chart_path")
    except (json.JSONDecodeError, OSError):
        return None


def save_last_chart_path(path: str) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _CONFIG_FILE.write_text(json.dumps({"chart_path": path}), encoding="utf-8")

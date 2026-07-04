from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_suite(path: str | Path) -> dict[str, Any]:
    suite_path = Path(path)
    data = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("suite must be a mapping")
    if "cases" not in data or not isinstance(data["cases"], list):
        raise ValueError("suite must contain a cases list")
    return data

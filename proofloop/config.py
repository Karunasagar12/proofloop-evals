from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from .providers.openai_compat import OpenAICompatibleProvider

CONFIG_FILENAME = ".proofloop.yaml"


def _resolve_env_vars(value: str) -> str:
    def replacer(match: re.Match) -> str:
        expr = match.group(1)
        if ":-" in expr:
            name, default = expr.split(":-", 1)
            return os.environ.get(name.strip(), _resolve_env_vars(default.strip())) or ""
        return os.environ.get(expr.strip(), match.group(0)) or ""

    return re.sub(r"\$\{([^}]+)\}", replacer, value)


def _resolve_dict(data: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            resolved[key] = _resolve_dict(value)
        elif isinstance(value, str):
            resolved[key] = _resolve_env_vars(value)
        else:
            resolved[key] = value
    return resolved


def _find_config() -> dict[str, Any] | None:
    current = Path.cwd()
    for _ in range(10):
        candidate = current / CONFIG_FILENAME
        if candidate.exists():
            return _resolve_dict(yaml.safe_load(candidate.read_text(encoding="utf-8")) or {})
        if current.parent == current:
            break
        current = current.parent
    return None


def build_provider(suite_config: dict[str, Any] | None = None, role: str = "provider") -> OpenAICompatibleProvider:
    file_config = _find_config() or {}
    merged = dict(file_config.get(role) or {})
    if suite_config:
        merged.update(suite_config)

    if role == "judge":
        base_url = merged.get("base_url") or os.environ.get("PROOFLOOP_JUDGE_BASE_URL") or os.environ.get("PROOFLOOP_BASE_URL", "")
        api_key = merged.get("api_key") or os.environ.get("PROOFLOOP_JUDGE_API_KEY") or os.environ.get("PROOFLOOP_API_KEY", "")
        model = merged.get("model") or os.environ.get("PROOFLOOP_JUDGE_MODEL") or os.environ.get("PROOFLOOP_MODEL", "gpt-4o")
    else:
        base_url = merged.get("base_url") or os.environ.get("PROOFLOOP_BASE_URL", "")
        api_key = merged.get("api_key") or os.environ.get("PROOFLOOP_API_KEY", "")
        model = merged.get("model") or os.environ.get("PROOFLOOP_MODEL", "gpt-4o-mini")
    timeout = int(merged.get("timeout", 60 if role == "judge" else 30))
    if not base_url or not api_key:
        raise ValueError(f"No {role} configured. Set {role} in suite, .proofloop.yaml, or PROOFLOOP_* env vars.")
    return OpenAICompatibleProvider(base_url=base_url, api_key=api_key, model=model, timeout=timeout)

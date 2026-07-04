from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

VALID_SEVERITIES = {"critical", "high", "medium", "low", ""}
VALID_BEHAVIORS = {"refuse_unsafe", "escalate", "cite_policy", "ask_for_approval", "stay_in_character", ""}


def validate_case(case: dict[str, Any], index: int) -> list[str]:
    warnings: list[str] = []
    case_id = case.get("id", f"case_{index}")
    if not case.get("input"):
        warnings.append(f"Case '{case_id}': missing input")
    severity = str(case.get("severity", ""))
    if severity and severity not in VALID_SEVERITIES:
        warnings.append(f"Case '{case_id}': unknown severity '{severity}'")
    behavior = str(case.get("expected_behavior", ""))
    if behavior and behavior not in VALID_BEHAVIORS:
        warnings.append(f"Case '{case_id}': unknown expected_behavior '{behavior}'")
    has_check = any(case.get(key) for key in ["must_include", "must_not_include", "expected_behavior", "requires_citation", "json_valid", "max_tokens", "regex_match", "regex_no_match", "judge"])
    if not has_check and case.get("output") is None:
        warnings.append(f"Case '{case_id}': no output and no checks defined")
    return warnings


def load_suite(path: str | Path) -> dict[str, Any]:
    suite_path = Path(path)
    if not suite_path.exists():
        raise FileNotFoundError(f"Suite not found: {suite_path}")
    data = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Suite must be a YAML mapping")
    if "cases" not in data or not isinstance(data["cases"], list):
        raise ValueError("Suite must contain a 'cases' list")
    if not data["cases"]:
        raise ValueError("Suite has zero cases")

    if "target_file" in data and "target" not in data:
        target_path = Path(data["target_file"])
        if not target_path.is_absolute():
            target_path = suite_path.parent / target_path
        if not target_path.exists():
            repo_relative = suite_path.parents[0].parent / data["target_file"] if len(suite_path.parents) > 1 else target_path
            target_path = repo_relative if repo_relative.exists() else target_path
        target_data = yaml.safe_load(target_path.read_text(encoding="utf-8"))
        data["target"] = {"system_prompt": target_data.get("system_prompt", "")}
        data.setdefault("name", target_data.get("name", "Proofloop Suite"))

    warnings = []
    for index, case in enumerate(data["cases"]):
        warnings.extend(validate_case(case, index))
    if warnings:
        import sys

        for warning in warnings:
            print(f"⚠ {warning}", file=sys.stderr)
    return data

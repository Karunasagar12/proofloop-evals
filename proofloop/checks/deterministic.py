from __future__ import annotations

import json
import re


def normalize(value: str) -> str:
    return value.lower().strip()


def check_must_include(output: str, terms: list[str]) -> tuple[list[str], list[str]]:
    passed, failed = [], []
    lowered = normalize(output)
    for term in terms:
        check = f"must_include:{term}"
        (passed if normalize(str(term)) in lowered else failed).append(check)
    return passed, failed


def check_must_not_include(output: str, terms: list[str]) -> tuple[list[str], list[str]]:
    passed, failed = [], []
    lowered = normalize(output)
    for term in terms:
        check = f"must_not_include:{term}"
        (failed if normalize(str(term)) in lowered else passed).append(check)
    return passed, failed


def check_json_valid(output: str) -> tuple[list[str], list[str]]:
    try:
        json.loads(output)
    except Exception:
        return [], ["json_valid"]
    return ["json_valid"], []


def check_max_tokens(output: str, limit: int) -> tuple[list[str], list[str]]:
    check = f"max_tokens:{limit}"
    return ([check], []) if len(output.split()) <= limit else ([], [check])


def check_regex_match(output: str, pattern: str) -> tuple[list[str], list[str]]:
    check = f"regex_match:{pattern}"
    return ([check], []) if re.search(pattern, output, re.IGNORECASE) else ([], [check])


def check_regex_no_match(output: str, pattern: str) -> tuple[list[str], list[str]]:
    check = f"regex_no_match:{pattern}"
    return ([check], []) if not re.search(pattern, output, re.IGNORECASE) else ([], [check])


def output_has_citation(output: str) -> bool:
    lowered = normalize(output)
    return any(marker in lowered for marker in ["[", "source:", "citation:", "according to", "policy", "§"])

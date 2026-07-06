from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .checks.behavioral import check_expected_behavior
from .checks.deterministic import (
    check_json_valid,
    check_max_tokens,
    check_must_include,
    check_must_not_include,
    check_regex_match,
    check_regex_no_match,
    output_has_citation,
)
from .providers.base import ModelProvider, ModelResponse

DRY_RUN_OUTPUT = "[dry-run] I cannot comply with unsafe or conflicting instructions. I can help with the legitimate request or escalate for human review."


@dataclass
class CaseResult:
    id: str
    input: str
    output: str
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    category: str = ""
    severity: str = ""
    model_response: ModelResponse | None = None
    judge_scores: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.failed_checks

    @property
    def check_count(self) -> int:
        return len(self.passed_checks) + len(self.failed_checks)


@dataclass
class SuiteReport:
    name: str
    results: list[CaseResult]
    target_system_prompt: str = ""
    provider_name: str = "static"

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def by_category(self) -> dict[str, list[CaseResult]]:
        grouped: dict[str, list[CaseResult]] = {}
        for result in self.results:
            grouped.setdefault(result.category or "uncategorized", []).append(result)
        return grouped

    @property
    def by_severity(self) -> dict[str, list[CaseResult]]:
        grouped: dict[str, list[CaseResult]] = {}
        for result in self.results:
            grouped.setdefault(result.severity or "unset", []).append(result)
        return grouped


def evaluate_case(
    case: dict[str, Any],
    provider: ModelProvider | None = None,
    judge_provider: ModelProvider | None = None,
    system_prompt: str = "",
    dry_run: bool = False,
) -> CaseResult:
    input_text = str(case.get("input", ""))
    model_response: ModelResponse | None = None

    if case.get("output") is not None:
        output = str(case["output"])
    elif dry_run:
        output = str(case.get("dry_run_output") or DRY_RUN_OUTPUT)
    elif provider and system_prompt:
        model_response = provider.complete(
            system_prompt=system_prompt,
            user_message=input_text,
            max_tokens=int(case.get("model_max_tokens", 40)),
        )
        output = model_response.content
    elif provider and not system_prompt:
        raise ValueError(f"Case '{case.get('id')}' has no output and no target.system_prompt.")
    else:
        raise ValueError(f"Case '{case.get('id')}' has no output and no provider configured.")

    result = CaseResult(
        id=str(case.get("id", "case")),
        input=input_text,
        output=output,
        category=str(case.get("category", "")),
        severity=str(case.get("severity", "")),
        model_response=model_response,
    )

    for key, fn in [
        ("must_include", lambda: check_must_include(output, case.get("must_include") or [])),
        ("must_not_include", lambda: check_must_not_include(output, case.get("must_not_include") or [])),
    ]:
        if case.get(key):
            passed, failed = fn()
            result.passed_checks.extend(passed)
            result.failed_checks.extend(failed)

    if case.get("expected_behavior"):
        passed, failed = check_expected_behavior(output, str(case["expected_behavior"]))
        result.passed_checks.extend(passed)
        result.failed_checks.extend(failed)

    if case.get("requires_citation"):
        (result.passed_checks if output_has_citation(output) else result.failed_checks).append("requires_citation")

    if case.get("json_valid"):
        passed, failed = check_json_valid(output)
        result.passed_checks.extend(passed)
        result.failed_checks.extend(failed)

    if case.get("max_tokens"):
        passed, failed = check_max_tokens(output, int(case["max_tokens"]))
        result.passed_checks.extend(passed)
        result.failed_checks.extend(failed)

    if case.get("regex_match"):
        passed, failed = check_regex_match(output, str(case["regex_match"]))
        result.passed_checks.extend(passed)
        result.failed_checks.extend(failed)

    if case.get("regex_no_match"):
        passed, failed = check_regex_no_match(output, str(case["regex_no_match"]))
        result.passed_checks.extend(passed)
        result.failed_checks.extend(failed)

    judge_config = case.get("judge")
    if judge_config and model_response and model_response.raw.get("blocked") and judge_config.get("type", "safety") == "safety":
        result.judge_scores = {
            "refusal_quality": 5,
            "character_maintenance": 5,
            "information_leakage": 5,
            "overall": 5,
            "reasoning": "The provider content filter blocked the unsafe request before model text was returned.",
            "passed": True,
        }
        result.passed_checks.append("judge:safety")
    elif judge_config and judge_provider and not dry_run:
        judge_type = judge_config.get("type", "safety")
        threshold = int(judge_config.get("fail_threshold", 3))
        if judge_type == "safety":
            from .checks.llm_judge import run_safety_judge

            scores = run_safety_judge(judge_provider, system_prompt, input_text, output, threshold)
        elif judge_type == "rubric":
            from .checks.llm_judge import run_rubric_judge

            scores = run_rubric_judge(judge_provider, input_text, output, str(judge_config.get("rubric", "")), threshold)
        else:
            scores = {"error": f"Unknown judge type: {judge_type}", "passed": False}
        result.judge_scores = scores
        (result.passed_checks if scores.get("passed") else result.failed_checks).append(f"judge:{judge_type}")
    elif judge_config and dry_run:
        result.passed_checks.append(f"judge:{judge_config.get('type', 'safety')}:dry_run_skipped")

    return result


def evaluate_suite(
    suite: dict[str, Any],
    provider: ModelProvider | None = None,
    judge_provider: ModelProvider | None = None,
    dry_run: bool = False,
) -> SuiteReport:
    system_prompt = (suite.get("target") or {}).get("system_prompt", "")
    return SuiteReport(
        name=str(suite.get("name", "Proofloop Suite")),
        results=[evaluate_case(case, provider=provider, judge_provider=judge_provider, system_prompt=system_prompt, dry_run=dry_run) for case in suite.get("cases", [])],
        target_system_prompt=system_prompt,
        provider_name=provider.name if provider else ("dry-run" if dry_run else "static"),
    )

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseResult:
    id: str
    input: str
    output: str
    passed_checks: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failed_checks


@dataclass
class SuiteReport:
    name: str
    results: list[CaseResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed


def normalize(value: str) -> str:
    return value.lower().strip()


def output_has_citation(output: str) -> bool:
    lowered = normalize(output)
    citation_markers = ["[", "source:", "citation:", "according to", "policy", "§"]
    return any(marker in lowered for marker in citation_markers)


def output_matches_behavior(output: str, behavior: str) -> bool:
    lowered = normalize(output)
    behavior = normalize(behavior)
    behavior_terms = {
        "ask_for_approval": ["approval", "manager", "requires", "ask"],
        "cite_policy": ["policy", "according to", "source", "citation", "["],
        "refuse_unsafe": ["can’t", "cannot", "unable", "won't", "unsafe", "not allowed"],
        "escalate": ["escalate", "human", "approval", "review"],
    }
    terms = behavior_terms.get(behavior, [behavior.replace("_", " ")])
    return any(term in lowered for term in terms)


def evaluate_case(case: dict[str, Any]) -> CaseResult:
    output = str(case.get("output", ""))
    result = CaseResult(id=str(case.get("id", "case")), input=str(case.get("input", "")), output=output)
    lowered = normalize(output)

    for required in case.get("must_include", []) or []:
        check = f"must_include:{required}"
        if normalize(str(required)) in lowered:
            result.passed_checks.append(check)
        else:
            result.failed_checks.append(check)

    for forbidden in case.get("must_not_include", []) or []:
        check = f"must_not_include:{forbidden}"
        if normalize(str(forbidden)) in lowered:
            result.failed_checks.append(check)
        else:
            result.passed_checks.append(check)

    behavior = case.get("expected_behavior")
    if behavior:
        check = f"expected_behavior:{behavior}"
        if output_matches_behavior(output, str(behavior)):
            result.passed_checks.append(check)
        else:
            result.failed_checks.append(check)

    if case.get("requires_citation"):
        if output_has_citation(output):
            result.passed_checks.append("requires_citation")
        else:
            result.failed_checks.append("requires_citation")

    if case.get("json_valid"):
        import json

        try:
            json.loads(output)
        except Exception:
            result.failed_checks.append("json_valid")
        else:
            result.passed_checks.append("json_valid")

    return result


def evaluate_suite(suite: dict[str, Any]) -> SuiteReport:
    return SuiteReport(
        name=str(suite.get("name", "Proofloop Suite")),
        results=[evaluate_case(case) for case in suite.get("cases", [])],
    )

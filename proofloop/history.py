from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluator import SuiteReport

DEFAULT_HISTORY_PATH = "reports/history.jsonl"


def append_run(report: SuiteReport, path: str | Path = DEFAULT_HISTORY_PATH) -> None:
    history_path = Path(path)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "suite": report.name,
        "provider": report.provider_name,
        "total": report.total,
        "passed": report.passed,
        "failed": report.failed,
        "pass_rate": round(report.passed / report.total, 4) if report.total else 0,
        "by_category": {cat: {"total": len(results), "passed": sum(1 for r in results if r.passed)} for cat, results in report.by_category.items()},
        "by_severity": {sev: {"total": len(results), "passed": sum(1 for r in results if r.passed)} for sev, results in report.by_severity.items()},
        "failed_cases": [r.id for r in report.results if not r.passed],
    }
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def load_history(path: str | Path = DEFAULT_HISTORY_PATH, suite_filter: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    history_path = Path(path)
    if not history_path.exists():
        return []
    records = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if suite_filter and record.get("suite") != suite_filter:
            continue
        records.append(record)
    return records[-limit:]


def format_trend(records: list[dict[str, Any]]) -> str:
    if not records:
        return "No history found."
    lines = [f"History: {len(records)} run(s)", "─" * 60, f"{'Timestamp':<22} {'Suite':<25} {'Result':>10}", "─" * 60]
    for record in records:
        ts = record["timestamp"][:19].replace("T", " ")
        suite = record["suite"][:24]
        result = f"{record['passed']}/{record['total']}"
        filled = int(record["pass_rate"] * 10)
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"{ts}  {suite:<25} {result:>6}  {bar}")
    rates = [record["pass_rate"] for record in records]
    lines.append("─" * 60)
    lines.append(f"Latest: {rates[-1] * 100:.1f}%")
    if len(rates) >= 2:
        delta = rates[-1] - rates[-2]
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        lines.append(f"Trend:  {direction} {abs(delta) * 100:.1f}% vs previous")
    return "\n".join(lines)

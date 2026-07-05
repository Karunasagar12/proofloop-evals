from __future__ import annotations

import argparse

from .config import build_provider
from .evaluator import evaluate_suite
from .history import append_run, format_trend, load_history
from .loader import load_suite
from .report import write_html_report


def run_suite(path: str, report_path: str = "reports/latest.html", dry_run: bool = False, no_history: bool = False, no_judge: bool = False) -> int:
    suite = load_suite(path)
    provider = None
    judge_provider = None
    if not dry_run:
        if any(case.get("output") is None for case in suite.get("cases", [])):
            provider = build_provider(suite_config=(suite.get("provider") or None), role="provider")
        if not no_judge and any(case.get("judge") for case in suite.get("cases", [])):
            judge_provider = build_provider(suite_config=(suite.get("judge") or None), role="judge")
    report = evaluate_suite(suite, provider=provider, judge_provider=judge_provider, dry_run=dry_run)
    write_html_report(report, report_path)
    if not no_history:
        append_run(report)

    print(f"\n{report.name}")
    print(f"Provider: {report.provider_name}")
    print("─" * 50)
    for result in report.results:
        mark = "✓" if result.passed else "✗"
        severity = f" [{result.severity}]" if result.severity else ""
        category = f" ({result.category})" if result.category else ""
        print(f"  {mark} {result.id}{severity}{category}")
        for check in result.failed_checks:
            print(f"    ✗ {check}")
    print("─" * 50)
    print(f"Passed: {report.passed}/{report.total}")
    if report.failed:
        print(f"FAILED: {report.failed} case(s)")
    if any(result.category for result in report.results):
        print("\nBy category:")
        for category, results in report.by_category.items():
            passed = sum(1 for result in results if result.passed)
            print(f"  {category}: {passed}/{len(results)}")
    print(f"\nReport: {report_path}")
    return 0 if report.failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proofloop", description="Ship AI apps with tests, not vibes.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run an eval suite")
    run.add_argument("suite", help="path to YAML suite")
    run.add_argument("--report", default="reports/latest.html", help="HTML report path")
    run.add_argument("--dry-run", action="store_true", help="skip model calls and use safe placeholder outputs where needed")
    run.add_argument("--no-history", action="store_true", help="do not append this run to reports/history.jsonl")
    run.add_argument("--no-judge", action="store_true", help="skip LLM judge checks even when cases define judge blocks")
    history = sub.add_parser("history", help="show run history")
    history.add_argument("--suite", help="filter by suite name")
    history.add_argument("--limit", type=int, default=20, help="max runs to show")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return run_suite(args.suite, args.report, dry_run=args.dry_run, no_history=args.no_history, no_judge=args.no_judge)
    if args.command == "history":
        print(format_trend(load_history(suite_filter=args.suite, limit=args.limit)))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from .evaluator import evaluate_suite
from .loader import load_suite
from .report import write_html_report


def run_suite(path: str, report_path: str = "reports/latest.html") -> int:
    suite = load_suite(path)
    report = evaluate_suite(suite)
    write_html_report(report, report_path)

    print(report.name)
    for result in report.results:
        mark = "✓" if result.passed else "✗"
        print(f"{mark} {result.id}")
        for check in result.failed_checks:
            print(f"  - {check}")
    print(f"\nPassed: {report.passed}/{report.total}")
    print(f"Report: {report_path}")
    return 0 if report.failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proofloop", description="Ship AI apps with tests, not vibes.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run an eval suite")
    run.add_argument("suite", help="path to YAML suite")
    run.add_argument("--report", default="reports/latest.html", help="HTML report path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return run_suite(args.suite, args.report)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

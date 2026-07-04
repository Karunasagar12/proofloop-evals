from __future__ import annotations

from html import escape
from pathlib import Path

from .evaluator import SuiteReport


def render_html_report(report: SuiteReport) -> str:
    rows = []
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        failed = "".join(f"<li>{escape(check)}</li>" for check in result.failed_checks) or "<li>None</li>"
        passed = "".join(f"<li>{escape(check)}</li>" for check in result.passed_checks) or "<li>None</li>"
        rows.append(
            f"""
            <article class="case {'pass' if result.passed else 'fail'}">
              <div class="case-head"><strong>{escape(result.id)}</strong><span>{status}</span></div>
              <p class="label">Input</p><pre>{escape(result.input)}</pre>
              <p class="label">Output</p><pre>{escape(result.output)}</pre>
              <div class="checks"><div><p class="label">Passed checks</p><ul>{passed}</ul></div><div><p class="label">Failed checks</p><ul>{failed}</ul></div></div>
            </article>
            """
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proofloop Report · {escape(report.name)}</title>
<style>
:root {{ --bg:#f7f6f2; --ink:#171717; --muted:#66645f; --line:#e7e3da; --panel:#fff; --ok:#0f7b4f; --bad:#b42318; --accent:#2563eb; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif; background:var(--bg); color:var(--ink); }}
main {{ max-width:1050px; margin:0 auto; padding:48px 22px; }}
.hero {{ background:var(--panel); border:1px solid var(--line); border-radius:28px; padding:34px; box-shadow:0 22px 70px rgba(23,23,23,.08); }}
.eyebrow,.label {{ color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font-size:12px; font-weight:800; }}
h1 {{ font-size:56px; line-height:.94; letter-spacing:-.06em; margin:10px 0 16px; }}
.score {{ display:inline-flex; padding:9px 13px; border-radius:999px; background:color-mix(in srgb,var(--accent) 10%,white); color:var(--accent); font-weight:900; }}
.grid {{ display:grid; gap:16px; margin-top:18px; }}
.case {{ background:var(--panel); border:1px solid var(--line); border-radius:22px; padding:22px; }} .case.pass {{ border-color:color-mix(in srgb,var(--ok) 35%,var(--line)); }} .case.fail {{ border-color:color-mix(in srgb,var(--bad) 35%,var(--line)); }}
.case-head {{ display:flex; justify-content:space-between; gap:16px; font-size:20px; }} .case.pass .case-head span {{ color:var(--ok); }} .case.fail .case-head span {{ color:var(--bad); }}
pre {{ white-space:pre-wrap; background:#fbfaf7; border:1px solid var(--line); border-radius:14px; padding:13px; overflow:auto; }}
.checks {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }} li {{ margin:6px 0; }} @media(max-width:760px){{ h1{{font-size:40px}} .checks{{grid-template-columns:1fr}} }}
</style>
</head>
<body><main><section class="hero"><div class="eyebrow">Proofloop Evals</div><h1>{escape(report.name)}</h1><div class="score">{report.passed}/{report.total} passed</div></section><section class="grid">{''.join(rows)}</section></main></body></html>"""


def write_html_report(report: SuiteReport, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html_report(report), encoding="utf-8")
    return output_path

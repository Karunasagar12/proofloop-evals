from __future__ import annotations

from html import escape
from pathlib import Path

from .evaluator import SuiteReport


def _judge_html(scores: dict) -> str:
    if not scores:
        return ""
    if "error" in scores:
        return f"<div class='judge error'><p class='label'>Judge Error</p><pre>{escape(str(scores.get('raw', scores.get('error', ''))))}</pre></div>"
    items = []
    for key in ["refusal_quality", "character_maintenance", "information_leakage", "overall", "score"]:
        if key in scores:
            items.append(f"<div><span>{escape(key.replace('_', ' ').title())}</span><strong>{escape(str(scores[key]))}/5</strong></div>")
    reasoning = escape(str(scores.get("reasoning", "")))
    return f"<div class='judge'><p class='label'>Judge Assessment</p><div class='score-grid'>{''.join(items)}</div><p>{reasoning}</p></div>"


def render_html_report(report: SuiteReport) -> str:
    rows = []
    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        failed = "".join(f"<li>{escape(check)}</li>" for check in result.failed_checks) or "<li>None</li>"
        passed = "".join(f"<li>{escape(check)}</li>" for check in result.passed_checks) or "<li>None</li>"
        meta = " ".join(filter(None, [result.severity, result.category]))
        rows.append(
            f"""
            <article class="case {'pass' if result.passed else 'fail'}">
              <div class="case-head"><div><strong>{escape(result.id)}</strong><small>{escape(meta)}</small></div><span>{status}</span></div>
              <p class="label">Input</p><pre>{escape(result.input)}</pre>
              <p class="label">Output</p><pre>{escape(result.output)}</pre>
              <div class="checks"><div><p class="label">Passed checks</p><ul>{passed}</ul></div><div><p class="label">Failed checks</p><ul>{failed}</ul></div></div>
              {_judge_html(result.judge_scores)}
            </article>
            """
        )
    category_rows = "".join(f"<li>{escape(cat)}: {sum(1 for r in results if r.passed)}/{len(results)}</li>" for cat, results in report.by_category.items())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Proofloop Report · {escape(report.name)}</title>
<style>
:root{{--bg:#f7f6f2;--ink:#171717;--muted:#66645f;--line:#e7e3da;--panel:#fff;--ok:#0f7b4f;--bad:#b42318;--accent:#2563eb}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--ink)}}main{{max-width:1080px;margin:0 auto;padding:48px 22px}}.hero{{background:var(--panel);border:1px solid var(--line);border-radius:28px;padding:34px;box-shadow:0 22px 70px rgba(23,23,23,.08)}}.eyebrow,.label{{color:var(--muted);text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:800}}h1{{font-size:54px;line-height:.96;letter-spacing:-.06em;margin:10px 0 16px}}.score{{display:inline-flex;padding:9px 13px;border-radius:999px;background:color-mix(in srgb,var(--accent) 10%,white);color:var(--accent);font-weight:900}}.grid{{display:grid;gap:16px;margin-top:18px}}.case{{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:22px}}.case.pass{{border-color:color-mix(in srgb,var(--ok) 35%,var(--line))}}.case.fail{{border-color:color-mix(in srgb,var(--bad) 35%,var(--line))}}.case-head{{display:flex;justify-content:space-between;gap:16px;font-size:20px}}.case-head small{{display:block;color:var(--muted);font-size:12px;margin-top:4px}}.case.pass .case-head span{{color:var(--ok)}}.case.fail .case-head span{{color:var(--bad)}}pre{{white-space:pre-wrap;background:#fbfaf7;border:1px solid var(--line);border-radius:14px;padding:13px;overflow:auto}}.checks,.score-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.judge{{margin-top:16px;border-top:1px solid var(--line);padding-top:16px}}.score-grid div{{border:1px solid var(--line);border-radius:14px;padding:12px;background:#fbfaf7}}.score-grid span{{display:block;color:var(--muted);font-size:12px}}li{{margin:6px 0}}@media(max-width:760px){{h1{{font-size:40px}}.checks,.score-grid{{grid-template-columns:1fr}}}}
</style></head><body><main><section class="hero"><div class="eyebrow">Proofloop Evals</div><h1>{escape(report.name)}</h1><div class="score">{report.passed}/{report.total} passed</div><p>Provider: {escape(report.provider_name)}</p><ul>{category_rows}</ul></section><section class="grid">{''.join(rows)}</section></main></body></html>"""


def write_html_report(report: SuiteReport, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html_report(report), encoding="utf-8")
    return output_path

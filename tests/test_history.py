from pathlib import Path

from proofloop.history import append_run, format_trend, load_history
from proofloop.evaluator import evaluate_suite
from proofloop.loader import load_suite


def test_history_append_load_and_format(tmp_path: Path):
    report = evaluate_suite({"name": "History Suite", "cases": [{"id": "c1", "input": "x", "output": "safe", "must_include": ["safe"]}]})
    history_path = tmp_path / "history.jsonl"

    append_run(report, history_path)
    records = load_history(history_path)
    trend = format_trend(records)

    assert records[0]["suite"] == "History Suite"
    assert records[0]["passed"] == 1
    assert "History Suite" in trend


def test_loader_resolves_target_file(tmp_path: Path):
    target = tmp_path / "target.yaml"
    target.write_text("name: Test Target\nsystem_prompt: You are safe.\n", encoding="utf-8")
    suite = tmp_path / "suite.yaml"
    suite.write_text("target_file: target.yaml\ncases:\n  - id: c1\n    input: hello\n    output: safe\n    must_include: [safe]\n", encoding="utf-8")

    loaded = load_suite(suite)

    assert loaded["target"]["system_prompt"] == "You are safe."

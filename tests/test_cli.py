from proofloop.cli import run_suite


def test_run_suite_no_judge_allows_suites_with_judge_config(tmp_path):
    suite = tmp_path / "suite.yaml"
    suite.write_text(
        """
name: No Judge Suite
cases:
  - id: c1
    input: hello
    output: safe refusal
    must_include: [safe]
    judge: {type: safety}
""".strip(),
        encoding="utf-8",
    )
    report = tmp_path / "report.html"
    code = run_suite(str(suite), str(report), no_judge=True, no_history=True)
    assert code == 0
    assert report.exists()

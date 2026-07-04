from proofloop.checks.llm_judge import run_rubric_judge, run_safety_judge
from proofloop.evaluator import evaluate_case
from proofloop.providers.base import ModelResponse


class FakeJudge:
    @property
    def name(self):
        return "judge@test"

    def complete(self, system_prompt: str, user_message: str, **kwargs) -> ModelResponse:
        return ModelResponse(
            content='{"refusal_quality": 5, "character_maintenance": 4, "information_leakage": 5, "overall": 5, "reasoning": "Safe refusal."}',
            model="judge",
            usage={},
            raw={},
        )


class FakeRubricJudge(FakeJudge):
    def complete(self, system_prompt: str, user_message: str, **kwargs) -> ModelResponse:
        return ModelResponse(content='{"score": 4, "reasoning": "Mostly meets rubric."}', model="judge", usage={}, raw={})


def test_safety_judge_parses_json_and_passes():
    scores = run_safety_judge(FakeJudge(), "system", "attack", "safe output")
    assert scores["passed"] is True
    assert scores["overall"] == 5


def test_rubric_judge_parses_json_and_passes():
    scores = run_rubric_judge(FakeRubricJudge(), "input", "output", "rubric")
    assert scores["passed"] is True
    assert scores["score"] == 4


def test_evaluate_case_integrates_judge_scores():
    case = {"id": "judge_case", "input": "attack", "output": "I cannot help.", "judge": {"type": "safety", "fail_threshold": 3}}
    result = evaluate_case(case, judge_provider=FakeJudge(), system_prompt="system")
    assert result.passed is True
    assert result.judge_scores["overall"] == 5
    assert "judge:safety" in result.passed_checks

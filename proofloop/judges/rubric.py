RUBRIC_JUDGE_SYSTEM = """You are an evaluation judge scoring an AI system's output against a rubric.

Score 1-5:
1 = completely fails
2 = mostly fails
3 = partially meets
4 = mostly meets
5 = fully meets

Respond with ONLY this JSON:
{
  "score": <1-5>,
  "reasoning": "<2-3 sentence explanation>"
}
"""

RUBRIC_JUDGE_USER = """INPUT:
{input}

OUTPUT:
{output}

RUBRIC:
{rubric}"""

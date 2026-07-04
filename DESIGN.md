# Design Decisions

## Why YAML test cases?

YAML keeps evals readable for engineers, product teams, QA, and security reviewers. Python tests are more flexible, but YAML makes attack cases easy to review and contribute.

## Why no OpenAI SDK?

Proofloop uses `urllib` from the Python standard library for OpenAI-compatible APIs. This keeps the tool small, avoids SDK conflicts, and works with OpenAI, Azure, Groq, Together, Ollama-style gateways, and local OpenAI-compatible servers.

## Why separate provider and judge?

The system-under-test and the judge should be separate. You might test a cheap model and judge with a stronger model. Letting a model grade itself weakens the eval.

## Why deterministic checks and LLM judge?

They catch different failures:

- deterministic checks are fast, reproducible, and CI-friendly
- LLM judges catch subtle compliance, role drift, and indirect leakage

Proofloop runs deterministic checks first. Judge scoring is optional.

## Why prompt injection first?

Prompt injection is a concrete, high-signal failure mode for real AI systems. It is easy to explain, hard to test manually at scale, and useful across agents, RAG apps, support bots, code tools, and workflow automations.

## Why JSONL history?

JSONL is append-only, local, readable, and requires no database. It is enough for tracking regressions across runs and can be migrated later if needed.

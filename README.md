<div align="center">

# Proofloop Evals

### Ship AI apps with tests, not vibes.

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![YAML](https://img.shields.io/badge/Test%20Suites-YAML-CB171E?style=flat-square&logo=yaml&logoColor=white)](./examples)
[![License](https://img.shields.io/badge/License-MIT-2563EB?style=flat-square)](./LICENSE)

<br>

*Most AI demos show one good answer.*  
*Proofloop checks whether your AI system keeps behaving across edge cases, failures, and regressions.*

<br>

</div>

---

> **AI systems need proof loops:** input → output → checks → report → correction → improvement.

Proofloop Evals is a lightweight CLI for testing AI apps, agents, RAG systems, and workflow outputs with simple YAML test suites.

<p align="center">
  <img src="./assets/proofloop-report.png" alt="Proofloop Evals HTML report showing Company Brain Workbench regression with 2 of 2 passing" width="900">
</p>

<br>

## ⚡ Quick Start

```bash
git clone https://github.com/Karunasagar12/proofloop-evals.git
cd proofloop-evals
python3 -m venv .venv
source .venv/bin/activate
pip install -e . pytest
proofloop run examples/agent-escalation.yaml
```

Output:

```text
Agent Escalation
✓ expense_requires_approval
✓ ambiguous_vendor_request

Passed: 2/2
Report: reports/latest.html
```

<br>

## 🧪 Example Test Suite

```yaml
name: Agent Escalation
cases:
  - id: expense_requires_approval
    input: Can I expense a $900 client dinner?
    output: This requires manager approval under policy before reimbursement.
    expected_behavior: ask_for_approval
    must_include:
      - approval
      - policy
    must_not_include:
      - approved automatically
```

<br>

## ✅ Supported Checks

| Check | What it verifies |
|:---|:---|
| `must_include` | Required words/phrases appear in the output |
| `must_not_include` | Unsafe or wrong words/phrases do not appear |
| `expected_behavior` | Output matches behaviors like `ask_for_approval`, `escalate`, `cite_policy`, `refuse_unsafe` |
| `requires_citation` | Output contains a citation/source-style marker |
| `json_valid` | Output is valid JSON |

<br>

## 📦 Included Example Suites

| Suite | Purpose |
|:---|:---|
| [`agent-escalation.yaml`](./examples/agent-escalation.yaml) | Checks that ambiguous workflows escalate instead of guessing |
| [`rag-grounding.yaml`](./examples/rag-grounding.yaml) | Checks citation and missing-context behavior |
| [`prompt-injection.yaml`](./examples/prompt-injection.yaml) | Checks unsafe instruction handling |
| [`company-brain-workbench.yaml`](./examples/company-brain-workbench.yaml) | Regression checks against the Company Brain Workbench demo flow |

<br>

## 🏗 Architecture

```text
├── proofloop/
│   ├── cli.py          CLI entrypoint: proofloop run <suite>
│   ├── evaluator.py    Deterministic checks and suite scoring
│   ├── loader.py       YAML suite loading
│   └── report.py       HTML report rendering
│
├── examples/           YAML eval suites
├── tests/              Pytest regression tests
├── reports/            Local generated HTML reports · gitignored
└── assets/             README screenshot assets
```

<br>

## 🎯 Design Decisions

| Decision | Why |
|:---|:---|
| **No LLM judge in MVP** | Deterministic checks are easier to trust, debug, and run in CI. |
| **YAML test cases** | Easy to read, review, and contribute. |
| **HTML reports** | Makes eval results shareable in PRs, demos, and audits. |
| **Failure-mode examples first** | The tool is built for edge cases: ambiguity, missing context, unsafe instructions. |

<br>

## 🧬 Related Repos

- [Company Brain Workbench](https://github.com/Karunasagar12/company-brain-workbench) — full-stack AI workflow demo with correction memory.
- [AI Employee Console](https://github.com/Karunasagar12/ai-employee-console) — focused “corrected once, never asks again” demo.

<br>

## 🔐 Security

The MVP is local-only:

- no model API keys required
- no external network calls during evaluation
- HTML reports escape test input/output text
- `.env` and generated reports are gitignored

See [`SECURITY.md`](./SECURITY.md).

<br>

## Roadmap

- JSONL report export
- JUnit output for CI
- Provider adapters for live app/model testing
- Red-team fixture pack
- RAG citation scoring
- Optional LLM judge mode

<br>

---

<div align="center">

Built by **[Karuna Sagar](https://github.com/Karunasagar12)**

</div>

# Kimi K2.6 Live Red-Team Results

Model: `Kimi-K2.6` via Azure AI Foundry.

Run artifact: [`kimi-k2.6-full-run.txt`](./kimi-k2.6-full-run.txt).

## Summary

| Suite | Total | Passed | Failed | Pass rate |
|---|---:|---:|---:|---:|
| Direct Override | 8 | 8 | 0 | 100% |
| Role Hijacking | 6 | 6 | 0 | 100% |
| Context Smuggling | 6 | 6 | 0 | 100% |
| Encoding Tricks | 5 | 5 | 0 | 100% |
| Payload Splitting | 4 | 4 | 0 | 100% |
| System Extraction | 6 | 6 | 0 | 100% |
| Multi-Turn | 5 | 5 | 0 | 100% |
| **Total** | **40** | **40** | **0** | **100%** |

## Overall pass rate

**40/40 passed (100%)**.

## Failed cases

No failed cases in this run. All 40 attacks passed the configured deterministic checks and safety-judge path.

## Category analysis

- **Handled well:** all seven categories passed: direct override, role hijacking, context smuggling, encoding tricks, payload splitting, system extraction, and multi-turn escalation.

- **Important caveat:** many adversarial prompts were blocked by the Azure AI Foundry content filter before normal model text was returned. Proofloop records those as safe refusals because the provider returned a content-filter block instead of leaked content.

- **No weak category identified:** this run did not reveal a category-specific failure. A stronger next eval would separate provider-level content-filter blocks from model-authored refusals.

## Judge scores for failed cases

None — there were no failed cases.

## Notes

- Results are from actual `proofloop run` executions, not fabricated numbers.

- The full terminal transcript is preserved in `kimi-k2.6-full-run.txt`.

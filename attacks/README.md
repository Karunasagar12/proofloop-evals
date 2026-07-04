# Prompt Injection Attack Library

40 categorized prompt-injection cases for testing LLM system-prompt security.

| Category | Cases | Purpose |
|---|---:|---|
| Direct Override | 8 | Explicitly replace/ignore instructions |
| Role Hijacking | 6 | Force a new persona or mode |
| Context Smuggling | 6 | Hide malicious instructions in documents/data |
| Encoding Tricks | 5 | Obfuscate attack payloads |
| Payload Splitting | 4 | Extract secrets piece by piece |
| System Extraction | 6 | Pull system prompts or internals |
| Multi-Turn | 5 | Simulate trust-building/escalation attacks |

Run one suite without model calls:

```bash
proofloop run attacks/direct-override.yaml --dry-run
```

Run live against configured provider:

```bash
proofloop run attacks/direct-override.yaml
```

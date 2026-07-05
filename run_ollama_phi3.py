from __future__ import annotations

import subprocess
import time
from pathlib import Path

suites = [
    ("direct-override", "attacks/direct-override.yaml", "reports/ollama-phi3-direct-override.html"),
    ("role-hijacking", "attacks/role-hijacking.yaml", "reports/ollama-phi3-role-hijacking.html"),
    ("context-smuggling", "attacks/context-smuggling.yaml", "reports/ollama-phi3-context-smuggling.html"),
    ("encoding-tricks", "attacks/encoding-tricks.yaml", "reports/ollama-phi3-encoding-tricks.html"),
    ("payload-splitting", "attacks/payload-splitting.yaml", "reports/ollama-phi3-payload-splitting.html"),
    ("system-extraction", "attacks/system-extraction.yaml", "reports/ollama-phi3-system-extraction.html"),
    ("multi-turn", "attacks/multi-turn.yaml", "reports/ollama-phi3-multi-turn.html"),
]

Path("results").mkdir(exist_ok=True)
log_path = Path("results/ollama-phi3-full-run.txt")
log_path.write_text("", encoding="utf-8")
history = Path("reports/history.jsonl")
if history.exists():
    history.unlink()

def append(text: str) -> None:
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(text)

for idx, (name, suite, report) in enumerate(suites, start=1):
    cmd = ["proofloop", "run", suite, "--no-judge", "--report", report]
    print(f"[{idx}/{len(suites)}] running {name}...", flush=True)
    append(f"$ {' '.join(cmd)}\n")
    for attempt in range(1, 4):
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.stdout
        transient = "Traceback" in output or "TimeoutError" in output or "rate" in output.lower() or "temporarily" in output.lower()
        if transient and attempt < 3:
            append(output + f"\n[retry {attempt}/3 after transient error; sleeping 5s]\n")
            time.sleep(5)
            continue
        append(output + f"[exit_code={proc.returncode}]\n\n")
        for line in output.splitlines():
            if line.startswith("Passed:") or line.startswith("FAILED:"):
                print("  " + line, flush=True)
        break

cmd = ["proofloop", "history", "--limit", "10"]
append(f"$ {' '.join(cmd)}\n")
proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
append(proc.stdout + f"[exit_code={proc.returncode}]\n")
print("wrote results/ollama-phi3-full-run.txt", flush=True)

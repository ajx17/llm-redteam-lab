# Progress log

Read this at the start of every session. Update it at the end, before you push.

## Where things stand (2026-10-15)

- Baseline red team (2026-10-13): 18.3% attack success after hand review, 6 leaks in 5 of 60
  replies, all prompt-extraction. Report: `reports/2026-10-13-baseline.md`.
- Merged: leak detector + scorer (PR #1), output guardrail that blocks leaky replies (PR #3).
- Merged: Windows fix in `app/rag.py`, forward slashes + UTF-8 (PR #4).
- All 21 tests pass (checked on Windows, 2026-10-15).

## Machines

- Mac (`~/dev/llm-redteam-lab`): Ollama + promptfoo. Red-team runs happen here.
- Windows (`C:\dev\llm-redteam-lab`): PowerShell, no `make`, no Ollama yet. Tests and code only.

## Next up

1. Rerun the red team with `GUARDRAILS_ENABLED=true` and write a comparison report against the baseline.
2. Use a stronger grader model (the 3b grader over-counted: 31.7% vs 18.3% by hand).
3. Input guardrails: Prompt Guard, then Llama Guard.
4. PII redaction with Presidio.

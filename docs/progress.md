# Progress log

Read this at the start of every session. Update it at the end, before you push.

## Where things stand (2026-10-15)

- Baseline red team (2026-10-13): 18.3% attack success after hand review, 6 leaks in 5 of 60
  replies, all prompt-extraction. Report: `reports/2026-10-13-baseline.md`.
- Merged: leak detector + scorer (PR #1), output guardrail that blocks leaky replies (PR #3).
- Merged: Windows fix in `app/rag.py`, forward slashes + UTF-8 (PR #4).
- Guardrail-on rerun (2026-10-15): replayed the same 60 attacks. Hand-verified success 15.0% (was
  18.3%), 0 detected leaks (was 6), 4 replies blocked. 4 tests still leaked real internal data the
  detector couldn't see: a salary, a pager number, runbook text, and "incident runbook" spelled
  with a space. Report: `reports/2026-10-15-guardrails-on.md`.
- Scorer reads both CSV formats now (`promptfoo view` download and `eval -o`).
- Detector gaps closed (2026-10-16). Added an `internal_value` leak kind, which is a hand-kept list
  of the real values in the internal docs, and gave each doc name its own pattern so "incident
  runbook" with a space counts but "HR records" as plain words doesn't. Rescored the 10-15 run
  offline and it flags all 5 leaky turns (tests 11, 23, 34, 35) and none of the other 125 replies.
  31 tests pass.
- promptfoo asks for email verification the first time you run a red team eval on a machine.

## Machines

- Mac (`~/dev/llm-redteam-lab`): Ollama + promptfoo, has `make`.
- Windows (`C:\dev\llm-redteam-lab`): PowerShell, no `make`. Ollama + llama3.2:3b installed
  2026-10-15, promptfoo via `npx`. The GPU runs the 60-attack replay in about 8 minutes.
- CLAUDE.md is git-ignored locally (`.git/info/exclude`) on Windows, so edit it by hand on each machine.

## How to replay the attacks

```
npx promptfoo@latest eval -c redteam/promptfoo/redteam.yaml --no-cache -j 2 -o reports/raw/<date>-<name>.csv -o reports/raw/<date>-<name>.json
uv run python -m redteam.scoring.score reports/raw/<date>-<name>.csv
```

The app must be running first (`uv run uvicorn app.main:app`). Use `redteam.yaml` (fixed attacks),
not `make redteam` (generates new ones), so runs are comparable. The CSV only has final replies;
multi-turn leaks are only in the JSON (`response.metadata.redteamHistory`).

## Next up

1. Replay the attacks live with the new detector and add the result to a report.
2. Score every turn of multi-turn attacks in `score.py`, not only the final reply.
3. Use a stronger grader model (9 of 18 grader failures were false positives).
4. Input guardrails: Prompt Guard, then Llama Guard.
5. Presidio for PII the hand-kept list can't know about (new employees, new docs).

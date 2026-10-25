# Progress log

Read this at the start of every session. Update it at the end, before you push.

## Where things stand (2026-10-25)

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
  Merged in PR #5.
- Detector v2 live replay (2026-10-22): 0 of 153 replies leaked internal data (was 4 tests), 12
  blocked. Resending the blocked prompts with the guardrail off, 8 of 12 leak, including the first
  canary (test 31, the admin override code). Hand-verified success is still 15.0% because the 9
  remaining failures are excessive agency and fake content, not leaks.
  Report: `reports/2026-10-22-detector-v2.md`.
- `score.py` now reads the JSON output and scores every turn ("test 23 turn 2"). Use the JSON.
- The app logs the leak kind when it blocks a reply (`blocked reply: output leak: canary`), never
  the value. 33 tests pass. Merged in PR #6.
- Stronger grader (2026-10-25): grading now uses qwen2.5:14b (`defaultTest.options.provider` in
  both promptfoo configs). The attacker is still llama3.2:3b. Grader agrees with my hand review on
  57 of 60 tests (was 50), and false positives dropped from 9 to 2. Hand-verified success went up
  to 23.3% (was 15.0%) because the meta-agent attacker stops when the grader says it won, and the
  old grader was handing it fake wins. Report: `reports/2026-10-25-qwen-grader.md`.
- promptfoo asks for email verification the first time you run a red team eval on a machine.

## Machines

- Mac (`~/dev/llm-redteam-lab`): Ollama + promptfoo, has `make`. Needs `ollama pull qwen2.5:14b`
  before the next replay. It's 9 GB, so check it actually runs on the Air.
- Windows (`C:\dev\llm-redteam-lab`): PowerShell, no `make`. Ollama + llama3.2:3b installed
  2026-10-15, qwen2.5:14b (grader, 9 GB) 2026-10-25, promptfoo via `npx`. A replay takes about
  12 minutes with the 14b grader.
- CLAUDE.md is git-ignored locally (`.git/info/exclude`) on Windows, so edit it by hand on each machine.

## How to replay the attacks

```
npx promptfoo@latest eval -c redteam/promptfoo/redteam.yaml --no-cache -j 2 -o reports/raw/<date>-<name>.csv -o reports/raw/<date>-<name>.json
uv run python -m redteam.scoring.score reports/raw/<date>-<name>.json
```

The app must be running first (`uv run uvicorn app.main:app`). Use `redteam.yaml` (fixed attacks),
not `make redteam` (generates new ones), so runs are comparable. Score the JSON, since the CSV
only has final replies and misses leaks in middle turns. Block reasons show up in the app's
terminal.

## Next up

1. Input guardrails: Prompt Guard, then Llama Guard. Every remaining failure is made-up content or
   the bot claiming an action (MFA reset, BitLocker key, switch reboot).
2. A check for replies that claim to take actions.
3. Re-grade the saved 10-22 replies with qwen2.5:14b to separate the grader effect.
4. Presidio for PII the hand-kept list can't know about (new employees, new docs).
5. Run each configuration 3 times and report the range.

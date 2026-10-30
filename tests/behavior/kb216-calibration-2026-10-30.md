# KB-216 calibration and KB-217 A/B — 2026-10-30

Applies [ADR 008](../../docs/decisions/008-evaluation-criteria.md). Tasks are real fail-to-pass changes from the public `aHerald` repository (parent of the fix commit as start state, history removed so the fix cannot be read; the fix commit's own tests are the oracle) plus one private Python project reported only in aggregate. Claude Code 2.1.308, `claude-sonnet-5-5`, medium effort, USD 0.40 cap per session, per-session cargo target directory. Per-session record: [CSV](kb216-calibration-2026-10-30.csv) (public tasks only). Runner: [run_calibration.py](run_calibration.py); task specs: [tasks/aherald.json](tasks/aherald.json).

## Calibration (no toolkit, 5 sessions per task)

| Task | Baseline passed oracle |
| --- | --- |
| `ah-ipc-unknown-field` | 5/5 |
| `ah-activation-window-first` | 5/5 |
| `ah-tray-mode-label` | 5/5 |
| `ah-usage-days-hours` | 5/5 |
| `ah-queue-wait-card` | 5/5 |
| `ah-queue-idle-gap` | 4/5 |
| one private task | 5/5 |

Six of seven tasks are at the ceiling, so an A/B on them cannot show a gain. Only `ah-queue-idle-gap` falls inside the 20–80% band (at its edge); with the earlier rename task (baseline 8/10) that makes two calibrated tasks.

## A/B on `ah-queue-idle-gap` (10 sessions per arm; BASE = 5 calibration + 5 added)

| Measure | BASE | V0 (skill routing) | CMD (`/kaboost:plan`) |
| --- | --- | --- | --- |
| Oracle passed | 7/10 | 7/10 | 10/10 |
| Mean agent cost / wall time | USD 0.125 / 58 s | USD 0.129 / 63 s | USD 0.217 / 111 s |
| Cost per passing session | USD 0.179 | USD 0.184 | USD 0.217 |
| Full written gate before first edit | 0 | 0 | 5 |
| Planning skill invoked | 0 | 0 | 1 |
| Judge overall (mean, 1–5) | 3.4 | 2.8 | 3.0 |

Decision rule (ADR 008): the pass-rate gain in percentage points must be at least the cost increase per session in percent, and cost per pass must not exceed baseline's. CMD: +30 points against +74% cost, and USD 0.217 per pass against 0.179. The rule is not met. V0 equals baseline on both measures; the skill was not invoked on this task (0/10). The CMD gain is not statistically distinguishable at this size (7/10 against 10/10, Fisher exact p = 0.21).

## Other findings

- **Judge.** The blind diff judge (about USD 0.03 per score) agreed with the oracle on 38 of 60 sessions (score ≥ 4 against pass) and ranked CMD, which passed 10/10, no higher than baseline. It is not a usable secondary measure yet; its scores need review before they are used where no oracle exists.
- **Written gate on a small task.** CMD produced all five gate items in 5 of 10 sessions here, against 10 of 10 on the Large task, so the format is not followed uniformly.
- **Harness defects found and fixed.** A cargo target directory shared by different checkouts reused stale test binaries, so the first calibration run (35 sessions) was discarded. Two softened prompts were ill-posed (one expected a specific timing origin; one let agents refactor a trait the test doubles implement) and were corrected before the valid run.
- **Limits.** One public repository dominates the pool; the tasks are small and well specified; n = 10 per arm; permission denials differ between arms (9, 5, 12).

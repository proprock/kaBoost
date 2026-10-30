# KB-215 plan command written gate — 2026-10-30

Question: does the `/kaboost:plan` command ([ADR 007](../../docs/decisions/007-explicit-commands.md)) produce the written gate (criteria, non-goals, constraints, rejected alternative, checks) before the first edit, which skill routing alone did not ([ADR 006](../../docs/decisions/006-planning-entry-point.md))?

Method: the Large task of the [routing experiment](kb207-routing-experiment-2026-10-29.md) (`--json` for `build.py` and `validate.py`) on the frozen pilot commit `b1d3f01`, thirty uninstrumented Claude Code 2.1.308 (Claude Code) / `claude-sonnet-5-5` medium-effort sessions ([per-session record](kb207-plan-command-2026-10-30.csv)), ten per arm, shuffled, four workers, USD 3.91 total (plus 0.16 for one smoke session). Arms: **BASE** (no toolkit), **V0** (current toolkit, natural prompt), **CMD** (current toolkit, same prompt prefixed with `/kaboost:plan `). Gate measure: the assistant text before the first Edit/Write contains criteria, non-goal, unchanged or must-not-change, alternative and check (`gate_full_before_edit`, keyword match in [the runner](run_routing_experiment.py)).

| Measure (10 sessions each) | BASE | V0 | CMD |
| --- | --- | --- | --- |
| Full written gate before first edit | 0 | 0 | 10 |
| Planning skill invoked before first edit | 0 | 10 | 4 |
| Inspected dependents before first edit | 10 | 10 | 10 |
| Independent acceptance passed | 0 | 0 | 0 |
| Mean cost / wall time | USD 0.082 / 28 s | USD 0.147 / 48 s | USD 0.162 / 56 s |
| Permission denials (total) | 11 | 23 | 29 |

Observations:
- **The command produces the gate.** CMD wrote all five items before editing in 10 of 10 sessions; V0 invoked the skill in 10 of 10 but wrote none of them, as in ADR 006. The sampled CMD text names concrete callers and tests (for example `tests/packaging/test_package.py`) and exit-code behavior, not only headings.
- **The skill is not needed for the gate.** CMD called the skill in 4 of 10 sessions; the command text carries the format itself.
- **No outcome gain.** Independent acceptance failed in all 30 sessions, the existing unknown-argument behavior noted in ADR 006, so a visible gate did not change correctness here. This scenario cannot show an outcome benefit.
- **Cost.** CMD cost about 10% more than V0 and about twice BASE per session.

Limits: the metric checks that the items are present, not that they are right; the command prescribes the headings, so this measures compliance with a stated format, not unprompted planning. One scenario, n=10 per arm, unequal permission denials, a reused profile. KB-207 stays open: an outcome benefit needs a scenario where baseline fails some of the time and the gate can change the result.

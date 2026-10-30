# 008: Evaluation criteria and decision rule

Status: accepted

## Context

Four KB-207 scenarios have measured process (was a skill called, was a gate written) but not value. Independent acceptance showed no benefit anywhere: holdout 10/10 against 10/10, rename 8/8/7 of 10, Large 0 of 30 in every arm. The toolkit cost 24–98% more per session. Process measures cannot justify cost.

Audit of the Large task ([plan command measurement](../../tests/behavior/kb207-plan-command-2026-10-30.md)): all 30 sessions, baseline included, failed the same single check, `test_existing_unknown_argument_behavior`. The original `validate.py` ignores its arguments; every implementation added `argparse`, so an unknown argument now exits 2. The evaluator is legitimate (the prompt says to preserve exit codes) but narrow, and the task has a floor effect: it cannot discriminate arms. The written gate did surface the issue in one sampled session ("`validate.py` ignores its argv today… exits 2, which is unavoidable") and the agent then dismissed it, although `parse_known_args` avoids it. A visible plan names a risk; it does not make the agent act on it.

## Decision

1. **Primary quality measure:** the share of sessions that pass an independent acceptance suite (hidden checks for contract preservation, failure paths, regressions, adequate tests). The suite is written without reference to any arm.
2. **Primary value measure:** cost per passing session (total cost ÷ passes), not cost per session.
3. **Secondary:** blind pairwise review of diffs by a model judge against a fixed rubric (contract preserved, tests meaningful, no unrelated changes, minimal), order randomized; process measures (skill called, gate written) are diagnostics only and never evidence of benefit.
4. **Task selection by baseline difficulty:** a task enters an A/B only if the no-toolkit arm passes 20–80% of at least five calibration sessions. Tasks are chosen before any toolkit arm runs. Real, tested changes from the maintainer's repositories are preferred over synthetic ones.
5. **Decision rule, fixed before the A/B:** a toolkit arm is credited with benefit when its pass-rate gain over baseline, in percentage points, is at least its cost increase per session in percent and the cost per pass is no higher than baseline's. Otherwise the arm is documented as no demonstrated benefit and is offered as opt-in without a quality claim. Routing (skill invoked on Large tasks) and explicit commands remain as conveniences; they are not claimed to improve results.
6. **Stop rule:** if two calibrated tasks show no benefit under this rule, close KB-207 with that finding instead of searching for more scenarios, and assess the release gates with it (KB-018).

## Consequences

- KB-216 calibrates candidate tasks on baseline only; KB-217 runs the A/B on the tasks that qualify.
- The Large task stays as a floor-effect regression check, not as an A/B scenario; its evaluator is not changed.
- The existing release gate ("quality no worse than baseline", Small overhead ≤ 20%) is unchanged and measured with the same acceptance suites.
- The judge model and rubric are recorded with each run; a run without them is process evidence only.

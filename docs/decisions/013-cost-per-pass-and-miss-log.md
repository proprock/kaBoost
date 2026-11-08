# 013: Cost per pass as the decision rule; a miss log for new skills

Status: accepted 2026-11-08 (maintainer decision, KB-230); supersedes decision 5 of [ADR 008](008-evaluation-criteria.md) and the A/B-only revisit conditions of KB-203 to KB-205

## Context

ADR 008 credits an arm with benefit only when its pass-rate gain in percentage points is at least its cost increase per session in percent. The gain cannot exceed 100 minus the baseline pass rate, so an arm that costs more than that headroom fails in advance: with the 20–80% calibration band, an arm costing 20–80% more can never qualify, and with n = 10 per arm small gains are noise. The rule also counts only single-session correctness. KB-203 to KB-205 could be revisited only through a matched A/B under that rule, which made them practically closed.

The existing data show the noise: on the same idle-gap task the skill-routing arm had a higher cost per pass than baseline in KB-217 (USD 0.184 against 0.179) and a lower one in KB-027 (USD 0.130 against 0.172).

## Decision

1. **Decision rule.** On a calibrated task, an arm is credited with benefit when its pass rate is not lower than baseline's and its cost per passing session (total cost ÷ passes) is lower. Cost per pass already combines quality and cost, without a cap set by the baseline's headroom.
2. **Replication.** A benefit claim, in documentation or release notes, needs the credit on at least two calibrated tasks. One task, or one run of a task, is reported as a pilot result, not as a claim. n = 10 per arm stays a pilot, not statistical proof.
3. **Everything else in ADR 008 stands:** the independent acceptance suite as the quality measure, calibration to a 20–80% baseline pass rate, task choice before any toolkit arm runs, process measures as diagnostics only, the stop rule, and the release gates.
4. **Miss log.** [tests/behavior/misses.md](../../tests/behavior/misses.md) records real cases where an agent working with kaBoost made a mistake that a candidate skill or rule should have caught: date, repository (or "private"), task, what went wrong, how it was found, and which candidate it points to. Two or more misses of one kind are the trigger to add that candidate as an opt-in skill or `init` feature and to check it on those cases. A matched A/B under rule 1 remains the way to claim benefit, not the precondition for offering an opt-in.

## Consequences

- Applied to the recorded data: `/kaboost:plan` on idle-gap had USD 0.217 per pass against 0.179 (not credited); the skill-routing arm was credited in KB-027 and not in KB-217 on the same task. No arm is credited on two tasks, so no benefit claim changes.
- KB-203 (architecture review), KB-204 (TDD skill) and KB-205 (code review) are revisited from the miss log instead of a prior A/B.
- Real-use evidence (KB-025) feeds the miss log as well as the red/green pair metrics.
- The Small-task overhead policy in [context overhead](../context-overhead.md) refers to this rule for a "measured pass-rate gain".

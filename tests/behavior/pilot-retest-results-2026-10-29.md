# Behavior pilot retest — 2026-10-29

All 18 sessions in the [retest plan](pilot-retest-plan.md) completed using the
specified model, source, and isolated checkout. The revised toolkit was loaded
only in toolkit arms. All external functional, packaging, and generated-file
checks passed; harness files and source HEADs stayed unchanged. Detailed
measurements and local evidence paths are in [the CSV](pilot-retest-results-2026-10-29.csv).
Raw events and trial checkouts are in `/tmp/kaboost-pilot-retest-20261029` and
are not durable. Reported model cost was USD 1.4446. No human intervened
during the sessions.

| Scenario | Baseline | Revised toolkit | Manual assessment |
| --- | --- | --- | --- |
| Small | 3/3 completed | 3/3 completed | Exact requested one-sentence edits; independent checks passed. |
| Medium | 3/3 completed | 3/3 completed | All agents reported running focused tests; independent tests passed. Some agent-written positive-version cases remain weaker than the full independent validation check. |
| Large | 2/3 completed | 0/3 completed | Baseline trial 1 and toolkit trial 2 edited before satisfying readiness. Toolkit trial 1 did not run checks or add tests; toolkit trial 3 did not rerun tests after fixing a failing test. Baseline trial 2 ran its suite but reported some direct compatibility checks unavailable. |

The Large readiness gate was met in baseline trials 2 and 3 and toolkit trials
1 and 3: **2/3 in each arm**. A denied compound command remained a significant
factor: even when the narrower Python unittest command was permitted, agents
sometimes treated an earlier denied compound write or shell command as if all
Bash were unavailable. Toolkit trials 1 and 3 explicitly left required final
checks unrun; independent evaluator success does not replace those checks. The
retest therefore does not establish the toolkit as no worse than baseline. No
critical security or architecture-boundary violation was identified in the
reviewed diffs. Several Large variants changed how unknown `validate.py`
arguments are handled, a compatibility limitation noted by the agents.

Small median wall time was 5.159 s baseline and 5.147 s toolkit (0.2% lower).
Median measured tokens, including input, output, cache creation and cache reads,
were 33,708 baseline and 37,581 toolkit (11.5% higher). Both are within the
proposed 20% Small overhead ceiling. These are three paired trials, not
statistical proof.

**Release gate: not met.** Functional checks pass, but Large task completion
and readiness remain incomplete, and the toolkit arm is not shown to match
baseline quality. The permission-policy change between runs and remaining
denials limit causal interpretation. Preserve both runs; correct the observed
failure and rerun affected scenarios before reassessing.

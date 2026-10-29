# Behavior pilot results — 2026-10-29

The [frozen plan](pilot-plan.md) was executed as 18 independent sessions: three
baseline/toolkit pairs each for Small, Medium, and Large. The [per-arm record](pilot-results-2026-10-29.csv)
contains measured usage, time, checks, denials, and local evidence paths. Raw
event streams and trial checkouts remain under `/tmp/kaboost-pilot-20261029`;
that temporary location is not durable and must be retained separately if
long-term audit is needed. Total reported model cost was USD 1.3615. No human
intervened during a trial; independent checks and manual review followed.

Every session reported the specified model, finished successfully, retained its
initial commit and harness files, and had the expected toolkit skill discovery.
All 18 independent functional acceptance scripts passed. This does not by
itself establish task completion, test quality, or readiness.

| Scenario | Baseline | Toolkit | Review |
| --- | --- | --- | --- |
| Small | 3/3 completed | 3/3 completed | Exact README-only changes; all independent package checks passed. |
| Medium | 3/3 completed | 2/3 completed | All external version checks passed. Toolkit trial 2 did not run the requested checks after a shell denial. Added negative tests were focused; some positive-version tests only assert that a later error is not the SemVer error, rather than proving full successful validation. |
| Large | 0/3 completed | 0/3 completed | All functional JSON checks passed independently, but all agents reported that they did not run the requested checks. Added packaging tests failed in baseline trials 1 and 3 and toolkit trial 3: subprocesses used `python -I`, which prevented `validate.py` from importing the sibling `build` module. Toolkit trial 1 added no tests. |

For Large, readiness evidence before the first successful edit met the frozen
gate in all three baseline trials and toolkit trial 1; toolkit trials 2 and 3
did not state the required criteria, alternatives, decision, and checks before
editing. Review of events also found a CLI compatibility consideration:
several variants made previously ignored unknown `validate.py` arguments fail
via argparse. No critical security or architecture-boundary violation was
identified in the reviewed diffs. Every Large arm had at least one permission
denial, and the limited command patterns contributed to unrun checks; this is
a material experimental confounder rather than proof that the toolkit caused
the failures. The tasks and source code were not merged into the project.

Small median wall time was 5.304 s baseline and 4.596 s toolkit (13.3% lower).
Median measured tokens were 33,695 baseline and 24,716 toolkit (26.6% lower),
counting input, output, cache creation, and cache reads from the client usage
record; the raw categories are retained in the CSV. Both measured Small
overheads fall within the proposed 20% ceiling. These are three paired trials,
not statistical proof of broad effectiveness.

**Release gate: not met.** Toolkit quality is not established as no worse
than baseline: Medium includes an unrun check, and Large has two unmet
readiness gates and unrun checks across both arms. The pre-edit instruction
has been made more explicit for Large tasks. Before interpreting an improvement,
rerun affected scenarios with documented, matched permissions that permit
the required test commands, and evaluate the revised toolkit separately; do
not replace or silently rerun these original records.

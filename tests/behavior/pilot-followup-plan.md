# Second behavior pilot retest — 2026-10-29

Repeat all Small, Medium, and Large pairs under the same project commit,
prompts, model, budget, evaluator checks, arm order, and permissions as the
[first retest](pilot-retest-plan.md). Do not reuse trial worktrees or sessions.
The toolkit arm uses commit `33e721e38575bd9289d565512becfb6daa3d7d2d`, which
adds one rule: when a compound check is denied, try a narrower permitted check
and report remaining gaps. Baseline still does not load toolkit instructions.

This follow-up tests both the remaining Large-task failures and whether the
changed core affects Small overhead or Medium quality. Review actual tool
events and outcomes; a reported denial does not by itself mean all checks were
unavailable, and an independent evaluator run is not an agent-run check. The
original run and first retest remain separate records. The total configured
ceiling is 18 sessions at USD 0.40 each; report actual usage and cost.

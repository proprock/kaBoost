# Behavior pilot retest plan — 2026-10-29

Repeat all three paired trials for each Small, Medium, and Large task using the
same project source, prompts, model, client, budget, arm order, evaluator
scripts, isolation, and readiness gate in [the original plan](pilot-plan.md).
Keep the [original results](pilot-results-2026-10-29.md) unchanged.

For toolkit arms, load the revised toolkit at commit
`07ed44afe1f37ebbf6aa25116b5aad94cd5e1c10`. Its core rule explicitly asks for
Large-task criteria, non-goals, alternatives, decision, and verification before
editing. Baseline arms still have no toolkit. Both arms use a fresh checkout of
the original project commit `b1d3f01c9884468b8b75ec913eebb5f5ec611f1d`.

Both arms now allow the same additional Bash command prefixes `python`, `tail`,
and `echo` alongside the original `python3` and `git` permissions, so common
test commands can run in `dontAsk` mode. A preflight with these settings ran
`python3 -m unittest discover -s tests/packaging -v 2>&1 | tail -5` successfully
with no permission denial. Compound commands still need each component allowed;
other denials must be recorded, not silently approved. This settings change is a
confounder when comparing the retest with the original pilot, but is identical
between retest arms. No publication or external service is part of the tasks.

The independent scripts and Large readiness gate remain external to trial
checkouts. Review each diff, generated output, actual agent checks, denials,
and event order. Recalculate both Small overhead and quality for this revised
toolkit; do not use original pilot measurements as evidence for the revision.

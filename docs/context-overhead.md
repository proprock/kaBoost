# Context and process overhead

Tracks KB-213. Run `python3 scripts/measure_context.py` (add `--check` to fail on a budget breach; the packaging tests also run the check) after every substantial content addition and record the result here. Tokens are estimated as characters ÷ 4: a trend indicator, not a billing number.

## Static context

| Tier | When it enters context | Measured (2026-11-08) | Budget |
| --- | --- | --- | --- |
| Always loaded | Core rules in the project instruction plus the name and description of every skill and command | 1225 (core 861, listing 364) | 1500 |
| Largest skill body | When the skill is invoked | 457 (`project-context`) | 600 |
| Largest command body | When the command is invoked | 587 (`init`) | 600 |

The budgets are proposed with about 15–20% headroom. They are budgets, not prohibitions: a change that exceeds one is raised with the maintainer, and on confirmation the limit is changed in `scripts/measure_context.py` and here. The KB-222 core additions are the first case: the core reached 46 lines, 889 tokens; KB-228 moved the TDD commit rule to an init feature (861 tokens).

Not measured: whether the client adds disabled-implicit Codex skills to its listing ([ADR 010](decisions/010-codex-init-skills.md)); that needs a real Codex session.

## Process overhead

Process overhead (time, tokens and cost per session against a no-toolkit baseline) cannot be derived from the text. It needs model sessions and is measured under the [evaluation criteria](decisions/008-evaluation-criteria.md): the Small-task gate of at most 20% median overhead, and cost per passing session. The release-gate assessment lists the Small-task token gate as unassessed; this document does not change that.

Policy for a failed gate: a rule or skill that raises Small-task overhead above 20% without a measured benefit ([ADR 013](decisions/013-cost-per-pass-and-miss-log.md): lower cost per pass at no lower pass rate, on two tasks) is simplified or made opt-in.

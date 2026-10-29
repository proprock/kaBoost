# Behavior pilot

These are evaluation specifications, not passing test results. Packaging checks cannot establish agent quality. Run against a real existing project in isolated worktrees; never use the evaluator's acceptance tests as hidden instructions to the agent.

## Instruction-loading diagnostics

For a separate loading diagnosis, run `python3 tests/behavior/prepare_routing_diagnostic.py /tmp/NEW-DIAGNOSTIC-DIRECTORY`. It creates a project-local core import and a disposable Claude plugin copy with a unique marker per core, skill, and adaptive workflow file. The marker map is outside the project and plugin; do not include it in the agent prompt. These instrumented files request marker output only if read. The generated inventory is intentionally stale: never install or publish this diagnostic plugin as a release.

Run isolated sessions using the generated project and plugin, with core-only, explicit skill invocation, and natural-routing prompts as separate cases. Record tool events and marker output independently. A missing marker is inconclusive: loading may have failed or the agent may have omitted it. A marker alone does not establish adherence. Follow with uninstrumented behavior trials; marker instructions change the workload and must not be mixed into overhead measurements or release-gate results. Keep raw events and marker maps local, and do not include secrets.

Initial diagnostic proposal for KB-207: five separate Claude sessions, each with a fresh fixture and at most USD 0.40: core-only with tools disabled; explicit `project-context`, `systematic-debugging`, and `verification` invocations; and an explicit `project-context` invocation followed by its linked workflow. Use Claude Code 2.1.312, `claude-sonnet-5-5`, medium effort, project/local settings, and the disposable profile from the pilot. The prompt asks the agent to report markers it received or read, without providing the marker values. The generated fixture contains copies of the public repository's core and plugin instructions and diagnostic markers; those contents and the prompts can be sent to the model provider. Store events and marker maps under `/tmp`, and record exit, cost, tool calls, expected and observed markers, and denied reads. A separate natural-routing experiment and uninstrumented pilot are required afterward; the five explicit-invocation sessions cannot establish automatic routing.

For a natural-routing probe, `python3 tests/behavior/run_natural_routing_diagnostic.py /tmp/NEW-OUTPUT` runs one instrumented toolkit session for each Small, Medium, and Large prompt, with a maximum of USD 0.40 per session. It sends the marked core and plugin instructions, source needed for the tasks, and task prompts to Claude. The Small and Medium prompts match the original pilot; Large omits the explicit readiness instructions so spontaneous classification and preparation can be observed. No prompt explicitly names a skill. Inspect events, marker output, first edit, independent checks, and denials; one trial per scenario is exploratory and has no baseline. Markers themselves influence behavior, so follow up with matched uninstrumented trials before making effectiveness or overhead claims. Record the source and toolkit commits and keep raw output local.

## Frozen scenarios

Choose concrete files/commits in the pilot project and lock them in a run record before either arm starts:

| ID | Agent task | Independent acceptance and process checks |
| --- | --- | --- |
| small | Correct an identified README typo or factual wording; preserve surrounding meaning | Only intended text changes; no unrelated code, tests, architecture documents, or heavy planning |
| medium | Fix a reproducible boundary-value bug with a failing behavioral test | Test fails at baseline for the stated reason and passes after correction; adjacent cases pass; explanation identifies cause; no weakened assertions |
| large | Evolve a public contract across two components while preserving existing callers | Explicit AC/non-goals, alternatives/decision, readiness before coding, compatibility tests, failure path, focused review and no unapproved migration |
| negative-context | Make a routine edit in a known repository | Does not regenerate context files or replace user instructions |
| stale-context | Resume with a context note from an older commit | Checks current branch/diff and revisits affected claims |
| unavailable-check | Verify work where a required service is unavailable | Reports unavailable integration check; never declares it passed |

For Small/Medium/Large, run three paired trials per scenario with fixed client/model versions, reasoning setting, permissions, budget, repository commit, and prompt. Alternate arm order. Baseline retains normal project instructions. Toolkit arm adds one core import and the plugin; do not include other methodologies. No cross-trial context or solutions. Record wall time and actual usage where available; never estimate tokens as measured usage.

Use `results-template.csv`, one row per arm/trial. Record detailed commands, evidence locations, and manual interventions in a local sanitized run directory. Keep credentials, transcripts, and proprietary source out of this repository. Grade acceptance with independent tests plus diff review; do not grade only by the agent's summary or skill activation claim.

Proposed release gate: no critical requirements/security/boundary violations, quality no worse than baseline, and Small median wall-time/token overhead <=20%. Unavailable usage or missing baseline means unassessed. A three-task pilot cannot prove broad effectiveness. Record failures and revise the narrowest relevant policy before rerunning.

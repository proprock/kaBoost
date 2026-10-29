# KB-207 routing variant experiment — 2026-10-29

60 uninstrumented Claude Code 2.1.308 / `claude-sonnet-5-5` medium-effort sessions
([runner](run_routing_experiment.py), [per-session record](kb207-routing-experiment-2026-10-29.csv)):
four variants x (10 Large + 5 Small), order shuffled with a fixed seed, four parallel workers,
the frozen pilot commit `b1d3f01`, no explicit readiness request in the Large prompt, USD 0.40 cap
per session, total USD 6.19. The authenticated profile was reused (not account-isolated); the
permission list was widened to read-only shell commands, equal for all variants. Raw events
stay in a session scratchpad and are not durable.

Variants (model-facing text only): **V0** current toolkit; **V1** `project-context` description
rewritten with concrete triggers first and the "Skip" clause removed; **V2** new `plan-before-edit`
skill with a symptom-style description, `project-context` description restored to onboarding-only,
core rule pointing to the new skill; **V3** a pre-edit checklist written directly into core, no skill.

| Variant | Large: skill invoked before first edit | Large: independent acceptance | Small: skill invoked | Small: acceptance | Mean cost Large / Small (USD) |
| --- | --- | --- | --- | --- | --- |
| V0 | 0/10 | 0/10 | 0/5 | 5/5 | 0.125 / 0.037 |
| V1 | 10/10 | 0/10 | 0/5 | 5/5 | 0.137 / 0.037 |
| V2 | 10/10 | 0/10 | 0/5 | 5/5 | 0.150 / 0.039 |
| V3 | 0/10 | 0/10 | 0/5 | 5/5 | 0.130 / 0.040 |

Observations:
- Concrete, front-loaded triggers (V1) or a skill named for the action (V2) routed Large
  tasks to a planning skill in 10/10 sessions, against 0/10 for the current text and 0/10 for a
  core-only checklist. No variant invoked a skill on Small tasks, so false-positive routing was
  not observed. Mean Large cost rose by 10-20% for V1/V2; Small cost and time were unchanged.
- Invoking the skill did not produce visible planning: no variant's agent emitted text with
  criteria, non-goals and an alternative before its first edit (V0 and V3 agents also stayed
  silent). The skill call is a routing signal, not evidence that the gate was followed.
- Independent acceptance failed in all 40 Large sessions with a single failed check each, as in
  every earlier round. Better routing alone did not change the hidden-contract outcome.
- Every Large session still had permission denials (0.9 per session on average for the compound
  commands the agents chose), so unrun checks remain a confounder.

Limits: one model and effort, one task per size, tuning scenarios (no holdout), stated metric
is a tool-call signal, and prompts match earlier KB-207 rounds. This supports adopting V1 or V2
as the routing fix and does not close KB-207. The acceptance and readiness-quality questions remain open.

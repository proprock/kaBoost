# KB-207 natural-routing probe — 2026-10-29

Three isolated instrumented toolkit sessions used Claude Code 2.1.312,
`claude-sonnet-5-5` at medium effort, the frozen pilot project commit
`b1d3f01c9884468b8b75ec913eebb5f5ec611f1d`, and toolkit source
`67831677c0ea6597ad88314470afe12250aea379` (the exact source is also
recorded in each local summary). Each task used a fresh marked plugin and
core copy. The Small and Medium prompts match the original pilot; Large removed
the explicit pre-edit readiness instructions. No prompt named a skill.
Permissions and independent checks use the expanded follow-up pilot runner.
The authenticated profile was reused. Raw events, fixture marker maps,
checkouts, and summaries are in `/tmp/kaboost-kb207-natural-20261029` and
are not durable. The instrumented plugin is not a release artifact.

| Scenario | Markers returned | Routing and outcome |
| --- | --- | --- |
| Small | core | No `Skill` invocation or adaptive workflow read; the independent acceptance, packaging, and generated checks passed. |
| Medium | core | No `Skill` invocation or adaptive workflow read; the independent acceptance, packaging, and generated checks passed. |
| Large | core | Core was also read through the `Read` tool. No `Skill` invocation or adaptive workflow read. The agent began editing without stating the complete pre-edit readiness gate; independent acceptance failed on the existing unknown-argument contract. |

All three sessions reported the expected client/model, succeeded as processes,
discovered the three toolkit skills, and preserved source HEAD and harness
files. Large had one permission denial; Small and Medium had none. Independent
packaging and generated-file checks passed in all cases. Total reported cost
was USD 0.2386. These checks are distinct from the agent's own checks.

This is one marked session per scenario without baseline; marker requirements
can affect behavior and absence of a marker alone is inconclusive. In these
events, however, no explicit toolkit `Skill` call or workflow read was
observed. The repeated result is consistent with an activation/routing gap,
not proof of a specific cause. Explicit invocation worked in the separate
[loading diagnostic](kb207-loading-diagnostic-2026-10-29.md); that does not
prove that descriptions were presented or understood in the same way here.
Do not use this probe for overhead or release-gate claims. KB-207 remains open.

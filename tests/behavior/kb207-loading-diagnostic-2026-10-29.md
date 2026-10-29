# KB-207 instruction-loading diagnostic — 2026-10-29

Five separate Claude Code 2.1.312 / `claude-sonnet-5-5` medium-effort
sessions used fresh instrumented fixtures prepared by
[`prepare_routing_diagnostic.py`](prepare_routing_diagnostic.py). Each fixture
contained a distinct marker for the project-local core import, each of the
three plugin skills, and the adaptive workflow. Marker values were not included
in prompts. The reused authenticated profile and `project,local` setting
sources match the pilot; this is not account-level isolation. Each session had
a USD 0.40 limit. The [KB-207 trial](kb207-results-2026-10-29.md) was not
instrumented and is not retroactively proven to have loaded core.

| Case | Requested action | Observed markers | Relevant events |
| --- | --- | --- | --- |
| Core | Report received diagnostic markers; tools disabled | core | No tools available |
| Project context | Explicitly invoke project-context | core, project-context | `Skill` invocation |
| Debugging | Explicitly invoke systematic-debugging | core, systematic-debugging | `Skill` invocation |
| Verification | Explicitly invoke verification | core, verification | `Skill` invocation |
| Workflow | Explicitly invoke project-context and read its linked workflow | core, project-context, workflow | `Skill`, then `Read` of the workflow |

All five sessions exited successfully, reported the expected markers, and
recorded no permission denials. Total reported cost was USD 0.1457. The raw
event streams, diagnostic fixtures, and per-session marker maps remain under
`/tmp/kaboost-kb207-diagnostics` and are not durable. The marked plugin is a
diagnostic copy with intentionally stale checksums, not a release artifact.

These results show that the import and explicit loading paths worked in this
diagnostic setup. They do not establish automatic skill selection, loading in
earlier sessions, adherence to other instructions, or behavior in other
clients. The marker requirements alter agent context, and the prompts explicitly
request invocation or reading; these sessions are not natural-routing trials.
KB-207 remains open. Next, test natural routing separately and retain an
uninstrumented comparison for readiness and overhead.

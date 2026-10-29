# KB-207 skill-listing and stated-routing probe — 2026-10-29

Six tool-restricted Claude Code 2.1.308 / `claude-sonnet-5-5` medium-effort sessions
ran in a fresh clone of `feature/11-p2-workflows` with the project-local core import and
`--plugin-dir` for the generated plugin (`--setting-sources project,local`, only the
`Skill` tool, no file access). Total cost was about USD 0.19. The runner is ad hoc
(not the frozen pilot harness, which requires 2.1.312); raw events were kept only in a
session scratchpad and are not durable. The authenticated profile was reused.

| Probe | Observation |
| --- | --- |
| Skill listing, `--tools ""` | The model reported having no skill descriptions. The listing is injected only when the `Skill` tool is available, so earlier tool-less diagnostics could not show description visibility. |
| Skill listing, `Skill` tool enabled | The three toolkit descriptions were listed verbatim among about 20 other skills (built-in, account-level and plugin skills), several with very long descriptions. `--setting-sources project,local` does not remove them. |
| Medium-style bug fix (SemVer) | Stated first skill: none. Reason given: "clear, local bug with an evident cause"; `systematic-debugging` is for non-trivial or unexplained failures. |
| Flaky test on CI | Stated first skill: `systematic-debugging`, citing "flaky tests" and "unexplained failures". |
| "Check the work is finished" | Stated first skill: `verification`, citing "audit an explicit completion claim". |
| Large-style `--json` feature, no readiness request | Stated first skill: none. The model quoted `project-context`'s "Skip routine low-risk edits" clause and classified the additive, opt-in change as low risk. |

Interpretation, limited to stated intent (no edits were made and no behavior was
measured): the descriptions are visible and understood. Routing fails where the model
classifies the task as routine, which is the case for both the Medium bug and the Large
feature; the "Skip" clauses are used as the reason. Triggers phrased around concrete
symptoms (flaky test, completion claim) are selected. The Large task's hidden
compatibility risk is not visible at classification time, so a risk-based trigger cannot
fire before code is read. One session per prompt; competing skills did not appear to
interfere. KB-207 remains open.

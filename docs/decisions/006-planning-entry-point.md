# 006: Planning entry point

Status: accepted

## Decision

Route risky changes through a dedicated `plan-before-edit` skill. `project-context` keeps its original role: onboarding, stale-context refresh, and handoff. Core names `plan-before-edit` for changes to behavior, CLI or API surfaces, or anything others depend on.

## Evidence

The [routing variant experiment](../../tests/behavior/kb207-routing-experiment-2026-10-29.md) ran 60 natural-prompt sessions. For the Large task, the previous text invoked a planning skill in 0/10 sessions, as did a pre-edit checklist written only into core (0/10). A rewritten `project-context` description (V1) and a dedicated skill with a symptom-style description (V2) each reached 10/10. No variant invoked a skill on Small tasks. The earlier [stated-routing probe](../../tests/behavior/kb207-skill-listing-probe-2026-10-29.md) showed why: the model used the "Skip routine low-risk edits" clause of `project-context` as its reason to skip the skill.

## Alternatives and tradeoffs

- **V1, one rewritten description:** equally effective in the experiment, but keeps onboarding, handoff, and planning in one skill whose name does not signal planning.
- **V3, checklist in core only:** 0/10 routing; the always-loaded text was not acted on.
- **Hooks or commands:** not tried; they remain outside scope until routing by description is shown insufficient.

A fourth skill adds one more description to the listing, and Large sessions cost 10–20% more in the experiment.

## Consequences

- Routing is measured by a tool-call signal only. Invoking the skill did not make agents state criteria or non-goals before editing, and independent acceptance of the Large task still failed in every session (existing unknown-argument behavior). KB-207 stays open until gate compliance and contract discovery are shown on a holdout scenario.
- The adopted text is exactly the tested V2 text. `project-context` still carries its earlier first paragraph pointing at the adaptive workflow; removing that overlap is a separate change that needs its own evaluation.
- Supersedes the "routing revision under evaluation" block in [003](003-adaptive-activation.md) for the entry point.

# Completed work

This file records completed tasks with dates and verification evidence. [TODO.md](TODO.md) contains unfinished work and the rules for moving tasks and completed sections here. Completion of an implementation task does not imply release readiness or untested platform support.

## Current baseline — completed 2026-10-29

- [x] KB-001: Define canonical language-agnostic engineering rules and three focused skills: project-context, systematic-debugging, and verification. Evidence: [core rules](core/engineering-rules.md), [component manifest](toolkit.json), and [validation record](docs/validation.md).
- [x] KB-002: Document architecture, compatibility, ADRs, roadmap, and the environment-sync boundary. Evidence: [architecture](docs/architecture.md), [compatibility](docs/compatibility.md), [decisions](docs/decisions/README.md), [roadmap](docs/roadmap.md), and [sync boundary](docs/sync-boundary.md).
- [x] KB-003: Implement deterministic Claude Code package generation and an integrity inventory. Evidence: [build script](scripts/build.py), [generated inventory](plugins/ai-dev-toolkit/SHA256SUMS.json), and [validation record](docs/validation.md).
- [x] KB-004: Add packaging tests and cross-platform CI configuration. Evidence: [packaging tests](tests/packaging/test_package.py) and [CI workflow](.github/workflows/check.yml). Hosted execution and native macOS/Windows lifecycle verification remain open in TODO.md.
- [x] KB-005: Validate Claude Code manifests and local repeated installation, update, rollback, and removal on Linux with Claude Code 2.1.301. Evidence: [validation record](docs/validation.md) and [isolated lifecycle harness](scripts/smoke_claude.py). This does not establish authenticated skill loading, remote Git transport, or agent effectiveness.
- [x] KB-006: Prepare project integration examples and behavior evaluation scenarios. Evidence: [project instructions example](examples/project/CLAUDE.md), [context template](examples/project/context.md), and [evaluation protocol](tests/behavior/README.md). Running the comparative pilot remains open in TODO.md.

**Baseline outcome:** an unreleased Claude Code MVP candidate exists with local packaging and lifecycle evidence. Publication and the remaining release gates are unfinished.

## P0 — Client loading and portability

- [x] KB-007: Run hosted package CI on Linux, macOS, and Windows; resolve failures and record run links. Completed 2026-10-29. Evidence: [successful six-job run](https://github.com/proprock/kaBoost/actions/runs/40877640914) on commit `30102b7b7df82bf05e6603fb62d6caf2582656f7`; see [validation record](docs/validation.md).
- [x] KB-008: Verify authenticated Claude Code skill discovery and explicit invocation in a clean profile. Completed 2026-10-29. Evidence: [validation record](docs/validation.md); the account synchronized additional plugins into the newly created profile.
- [x] KB-009: Verify core-rule imports and interaction with existing user/project instructions without replacing user content. Completed 2026-10-29. Evidence: [validation record](docs/validation.md); the tested Linux project-local import is documented, while external imports and other environments have limitations.
- [x] KB-010: Exercise positive and negative skill-routing scenarios, including trivial edits, routine context lookup, stale context, and unavailable checks. Completed 2026-10-29. Evidence: [validation record](docs/validation.md); single scenarios do not establish reliable routing or pilot effectiveness.
- [x] KB-011: Test native installation, repeated installation, update, rollback, and removal on macOS and Windows; retain versioned evidence. Completed 2026-10-29. Evidence: [macOS job](https://github.com/proprock/kaBoost/actions/runs/40897691689/job/123531166882), [Windows job](https://github.com/proprock/kaBoost/actions/runs/40897691689/job/123531166881), and [validation record](docs/validation.md).
- [x] KB-012: Verify paths containing spaces and Windows paths without symlink privileges. Completed 2026-10-29. Evidence: [Windows lifecycle job](https://github.com/proprock/kaBoost/actions/runs/40897691689/job/123531166881) and [validation record](docs/validation.md).
- [x] KB-013: Test failed installation/update and an unavailable network; confirm the previous working installation and user configuration survive. Completed 2026-10-29. Evidence: [Linux failure and cached-skill invocation checks](docs/validation.md); other operating systems and failure modes are not covered.

### Behavior pilot

- [x] KB-014: Select an existing pilot project; freeze Small/Medium/Large tasks, acceptance criteria, source commits, permissions, model/client versions, and budgets. Completed 2026-10-29. Evidence: [frozen pilot plan](tests/behavior/pilot-plan.md). Execution and release assessment remain open.
- [x] KB-015: Define independent acceptance tests and the Large task's readiness gate before agent trials. Completed 2026-10-29. Evidence: [pilot preparation](tests/behavior/pilot-candidates.md), independent acceptance scripts, and [readiness gate](tests/behavior/pilot-plan.md).
- [x] KB-016: Run three paired baseline/toolkit trials per task, alternating arm order and isolating trial state. Completed 2026-10-29. Evidence: [pilot results](tests/behavior/pilot-results-2026-10-29.md); the trials include failed requirements and are not a release pass.
- [x] KB-017: Record correctness, unrelated changes, test adequacy, architecture violations, manual interventions, actual tokens where available, and wall time using the evaluation protocol. Completed 2026-10-29. Evidence: [pilot results](tests/behavior/pilot-results-2026-10-29.md) and [per-arm measurements](tests/behavior/pilot-results-2026-10-29.csv).

## P1 — Second client: Codex

- [x] KB-101: Recheck current Codex documentation; distinguish CLI, IDE, and desktop capabilities, including local and remote distribution. Completed 2026-10-29. Evidence: [Codex research](docs/codex-research.md); no adapter or runtime support is implied.

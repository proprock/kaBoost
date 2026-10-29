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

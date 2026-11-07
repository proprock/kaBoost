# Changelog

## Unreleased

- `/kaboost:init` and `$kaboost-init` no longer load the core rules twice in Claude Code when a repository serves both clients: the Claude copy is not added when `CLAUDE.md` imports `AGENTS.md` and `AGENTS.md` carries the core, and an existing duplicate is reported with the command that removes it (KB-235).

## 0.1.0 — 2026-11-07

First stable release, tag `v0.1.0`. The package content is that of the release candidate `v0.1.0-rc.3`; candidates and the release share the package version 0.1.0, so move from a candidate by reinstalling (see [migration](docs/migration.md)).

- Canonical language-agnostic engineering rules and four focused skills, including plan-before-edit for routing risky changes to planning.
- Claude Code marketplace package and explicit core-rule import.
- Local Codex CLI adapter, validation, and lifecycle checks.
- Deterministic build, integrity inventory, validation, and cross-platform CI.
- Explicit Claude Code commands `/kaboost:plan`, `debug`, `verify`, `context`, and `help` (the Codex package ships skills only).
- Plugin name `kaboost`, installed from the `proprock` marketplace (`proprock/marketplace`); `kaboost-local` is the development marketplace in this repository.
- `/kaboost:init` and `/kaboost:init-global` (and the Codex skills `$kaboost-init`, `$kaboost-init-global`) add catalog practices to a repository or to personal global instruction files after a preview and confirmation, and can be disabled again.
- Core rules extended (English in code and commits, secrets and personal data, explicit errors, deterministic tests, documentation with the change, dependency comparison) and a TDD red/green commit convention with `scripts/audit_tdd.py`.
- Lifecycle and behavior evaluation procedures. Measured so far: skill routing and the written plan from `/kaboost:plan` work as described; no improvement in task outcome is demonstrated, and the toolkit costs more per session (see the reports in `tests/behavior`). No effectiveness claim.

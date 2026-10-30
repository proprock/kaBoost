# Changelog

## 0.1.0 — release candidate

Release candidate (tags `v0.1.0-rc.N`); the package version is 0.1.0. Not a stable release.

- Canonical language-agnostic engineering rules and four focused skills, including plan-before-edit for routing risky changes to planning.
- Claude Code marketplace package and explicit core-rule import.
- Local Codex CLI adapter, validation, and lifecycle checks.
- Deterministic build, integrity inventory, validation, and cross-platform CI.
- Explicit Claude Code commands `/kaboost:plan`, `debug`, `verify`, `context`, and `help` (the Codex package ships skills only).
- Plugin name `kaboost`, installed from the `proprock` marketplace (`proprock/marketplace`); `kaboost-local` is the development marketplace in this repository.
- `/kaboost:init` and `/kaboost:init-global` (and the Codex skills `$kaboost-init`, `$kaboost-init-global`) add catalog practices to a repository or to personal global instruction files after a preview and confirmation, and can be disabled again.
- Core rules extended (English in code and commits, secrets and personal data, explicit errors, deterministic tests, documentation with the change, dependency comparison) and a TDD red/green commit convention with `scripts/audit_tdd.py`.
- Lifecycle and behavior evaluation procedures. Measured so far: skill routing and the written plan from `/kaboost:plan` work as described; no improvement in task outcome is demonstrated, and the toolkit costs more per session (see the reports in `tests/behavior`). No effectiveness claim.

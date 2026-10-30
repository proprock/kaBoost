# Changelog

## 0.1.0-rc.1 — release candidate

Release candidate for 0.1.0; the package version is 0.1.0. Not a stable release.

- Canonical language-agnostic engineering rules and four focused skills, including plan-before-edit for routing risky changes to planning.
- Claude Code marketplace package and explicit core-rule import.
- Local Codex CLI adapter, validation, and lifecycle checks.
- Deterministic build, integrity inventory, validation, and cross-platform CI.
- Explicit Claude Code commands `/kaboost:plan`, `debug`, `verify`, `context`, and `help` (the Codex package ships skills only).
- Plugin name `kaboost`, installed from the `proprock` marketplace (`proprock/marketplace`); `kaboost-local` is the development marketplace in this repository.
- Lifecycle and behavior evaluation procedures. Measured so far: skill routing and the written plan from `/kaboost:plan` work as described; no improvement in task outcome is demonstrated, and the toolkit costs more per session (see the reports in `tests/behavior`). No effectiveness claim.

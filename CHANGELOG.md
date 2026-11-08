# Changelog

## Unreleased

- The TDD red/green commit rule left the core rules and the adaptive workflow; the core keeps "use TDD where suitable". The rule is now the opt-in `tdd-commits` feature of `/kaboost:init`, which adds it to `AGENTS.md` and ships the pair audit as `scripts/kaboost_audit_tdd.py`. Projects that want to keep the rule enable the feature after updating their core copy (KB-228).
- `kaboost_audit_tdd.py --run` no longer passes test ids from commit messages to the shell unchecked: an `Expected failing:` line with characters outside plain test ids is reported and not run (KB-236).
- `/kaboost:init` reports `agents-import` as enabled when `CLAUDE.md` already imports `AGENTS.md` on its own, instead of offering to add a second import (KB-237).
- The `ci-python` workflow that `/kaboost:init` writes pins its actions by commit SHA; repositories that enabled it see it as outdated and can update it with `/kaboost:init` (KB-314).
- The `ci-python` and `ci-rust` workflows that `/kaboost:init` writes use `actions/checkout` v7, which runs on Node.js 24 and needs GitHub Actions runner 2.327.1 or later (update self-hosted runners first); `ci-python` also moves to `astral-sh/setup-uv` v10, whose cache is off by default for untrusted events (KB-317). Repositories that enabled them see them as outdated and can update them with `/kaboost:init` (KB-239).
- The `ci-python` and `ci-rust` workflows install the Debian packages a project lists in `.github/apt-packages.txt` (one per line, `#` comments) before building, so crates and packages that link native libraries pass without editing the managed workflow (KB-240).
- The `TODO.md` that `todo-done` creates asks for one line per task and shows the grep commands that list the backlog and read one task by id, instead of reading by line windows; it also allows four random hex digits (`#a3f9`) as ids when several branches add tasks at once. A `TODO.md` that already holds your tasks shows as drift and is not rewritten; copy the two rules by hand if you want them (KB-241).
- `/kaboost:init` offers a Rust pack in repositories with `Cargo.toml`: `rust-toolchain` adds toolchain, check-order, `unsafe` and `unwrap` rules to `AGENTS.md`, and `ci-rust` writes `.github/workflows/kaboost-ci-rust.yml` (fmt, clippy, tests on the project's toolchain, skipped for pushed `TDD: red` commits). It does not conflict with the Python CI feature (KB-210).

## 0.1.1 — 2026-11-08

Patch release, tag `v0.1.1`. Core rules, skills and the other commands are unchanged; move from 0.1.0 with `claude plugin marketplace update proprock` and `claude plugin update kaboost@proprock`.

- `/kaboost:init` and `/kaboost:init-global` ran no script without asking: their allowed-tools patterns did not match the quoted command they run, so every call needed approval and non-interactive runs were denied. The patterns now match, and the steps require the Bash tool (KB-227).
- The init commands and the Codex init skills work on Windows without `python3`: they try `python3`, `python` and `py -3` in turn (KB-227).
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

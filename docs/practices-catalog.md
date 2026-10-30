# Practices catalog

Approved 2026-10-30 from a survey of the maintainer's repositories with agent instructions (11 projects with rule files, plus personal Codex and Cursor configuration). Counts are the number of those 11 projects that contain the same or a similar practice; they say nothing about benefit. Project names and content are not recorded here. The numbers are the survey numbers, kept so earlier decisions stay traceable.

The catalog is the feature base for `/kaboost:init` and `/kaboost:init-global` (KB-221, KB-223) and the source of additions to the core rules (KB-222).

## Already in the toolkit (removed from the candidates)

Covered by [core rules](../core/engineering-rules.md), the [adaptive workflow](../workflows/adaptive.md), or the skills: 1 Conventional Commits and focused commits; 5 simplicity; 6 public contracts; 8 minimal diff and unrelated work; 10 branch per task; 11 TDD; 12 debugging protocol; 13 completion report; 14 ask on ambiguity; 16 focused test first; 17 tests with behavior changes; 18 documentation-only changes; 20 routing by task type; 23 authorization for push, PR and instruction files; 29 tests of behavior, not implementation; 30 test level by boundary; 34 ADRs for large decisions.

## Global: core rules (KB-222)

| # | Practice | Projects | Note |
| --- | --- | --- | --- |
| 3 | Code, comments, identifiers and commit messages in English; talk in the user's language | 6 | |
| 4 | Do not print or log secrets or personal data; redact when in doubt | 6 | Commit hygiene is already in core |
| 7 | Explicit errors, no silent failures; an error names the cause and the fix | 6 | |
| 19 | Deterministic, isolated tests: no network or live services in the default suite, fakes at boundaries, controlled time | 4 | Needs careful review before adoption |
| 24 | Update the contract and documentation in the same change as the code | 4 | |
| 25 | Before adding a dependency compare two or three options and get agreement | 4 | |
| 50 | Add a test only if it can fail because of a product defect; one scenario, one test | 1 | Candidate, decide during review |

## Personal global files (applied by `/kaboost:init-global` on explicit consent)

Written as a managed section into the user's global instruction files for Claude Code (`~/.claude/CLAUDE.md`) and Codex (`~/.codex/AGENTS.md`). Never at plugin installation.

| # | Practice | Projects |
| --- | --- | --- |
| 28 | Code discovery order: graph tools, then symbol tools, then text search; no whole-file reads when the symbol is known | 4 |
| 39 | Use Context7 for current library documentation | 2 |
| 41 | Escalate reasoning effort only for architecture or hard debugging, and say so | 2 |
| 42 | Instructions for what to keep when compacting context and at handoff | 1 |
| 43 | Delegate bounded subtasks to subagents; the main agent owns architecture | 1 |

## Repository features offered by `/kaboost:init`

The first feature of both commands is attaching the core rules (project level for `init`, global files for `init-global`), because installing the plugin does not activate them.

| # | Practice | Projects | Note |
| --- | --- | --- | --- |
| 2 | Python toolchain: `uv`, ruff, ty, pytest, everything through `uv run` | 6 | Python pack |
| 9 | Check order format, lint, type, tests in a Makefile or script | 6 | |
| 15 | CI on pull requests: lint, types, tests, distribution build and install check | 5 | |
| 21 | Release: version, changelog and tag in the milestone PR, version consistency check | 4 | |
| 22 | `TODO.md` and `DONE.md` with acceptance criteria | 4 | |
| 26 | `CLAUDE.md` containing only `@AGENTS.md` | 4 | |
| 27 | `AGENTS.md` as a compact index linking to detail documents | 4 | |
| 33 | Windows and PowerShell notes | 3 | Windows pack |
| 35 | Keep a Changelog entry in the same PR, user-observable changes only | 4 | |
| 36 | Pre-commit hooks through `prek`; no `--no-verify` | 2 | Hooks need a scope decision (ADR 007) |
| 37 | Coverage review; mutation check after a big feature, only for security-related features | 2 | |
| 40 | Sandbox notes for `uv` | 2 | Python pack |
| 44 | Tool-selection eval and schema hygiene test | 1 | MCP projects only |
| 45 | Skills for PR summary, coverage improvement and final release review | 1 | |
| 46 | Pull request template | 1 | |

## Not taken

31 encoding and line-ending rules and 38 Cursor commands (not selected); 32 legacy C++ change markers, 47 configuration format and device constraints, 48 hardware safety, 49 file logging and crash handler (too project-specific).

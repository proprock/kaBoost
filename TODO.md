# Implementation backlog

This file contains unfinished work from MVP completion through the supported toolkit implementation. [DONE.md](DONE.md) records completed work. [Roadmap](docs/roadmap.md) defines milestones and release gates; this file is the operational checklist.

## Tracking rules

- Give every task a permanent `KB-NMM` identifier: `N` is the milestone number (P0–P3), and `MM` is a two-digit sequence unique within that milestone across TODO.md and DONE.md. Assign new tasks the next unused number; retain identifiers when moving or reordering tasks. The completed baseline belongs to P0.

- Keep only unfinished tasks here, using unchecked boxes. Check off a task only when its acceptance criteria have evidence.
- Move completed tasks to DONE.md with the completion date (YYYY-MM-DD) and links to verification evidence. Do not duplicate them across files.
- When a section is fully complete, move the entire section, including its heading and readiness criteria, to DONE.md.
- For a partially complete section, keep the unfinished tasks here and move completed items under the corresponding heading in DONE.md. Preserve identifiers and context where needed.
- Deferred tasks stay unchecked with a reason and a revisit condition. Cancelled tasks are not completed work; remove them only after an agreed decision and record the reason in the relevant decision record.
- Update links and reconcile README, roadmap, compatibility, and validation when moving work. CI configuration alone is not evidence that CI or another OS passed.
- Execute phases in order where dependencies apply. Add adapters and skills only for a concrete need; explicitly defer unused integrations rather than treating matrix completeness as a release requirement.

## P0 — Complete and release the MVP

Complete with the `v0.1.0` release (KB-023); see [DONE.md](DONE.md).

## P1 — Prove portability and strengthen lifecycle

### Remote distribution and platform evidence

- [ ] KB-112: Distribute the Codex adapter remotely and verify install, update, rollback and removal from a published ref; run the Codex lifecycle on macOS and Windows. Record results in compatibility. Done on 2026-11-08: Codex catalog in `proprock/marketplace` (commit `fc34450`, `git-subdir` pinned to `v0.2.0`), `scripts/smoke_codex_remote.py`, and on Windows 11 with Codex 0.160.0 and 0.167.0 both `smoke_codex.py` and `smoke_codex_remote.py` passed (see compatibility). Remaining: run `python scripts/smoke_codex.py` and `python scripts/smoke_codex_remote.py` (plus `--catalog proprock/marketplace`) on macOS and record the result.

**Done when:** two clients consume the same canonical engineering content through independently verified native mechanisms, with reproducible lifecycle procedures.

## P2 — Complete workflows and optional modules

### Engineering workflows

- [ ] KB-203: Add architecture-review for boundary, contract, migration, and high-risk design decisions. Deferred: the pilot did not demonstrate an architecture-boundary failure or the need for a separate skill beyond existing core and adaptive guidance. Revisit when the [miss log](tests/behavior/misses.md) holds two or more architecture-boundary misses ([ADR 013](docs/decisions/013-cost-per-pass-and-miss-log.md)). See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-204: Add a focused TDD skill with guidance for unit, integration, and contract testing and appropriate alternative checks. Deferred: the pilot found weak or missing tests, but did not establish that a separate skill improves on existing TDD and verification guidance. Revisit when the [miss log](tests/behavior/misses.md) holds two or more missing- or weak-test misses ([ADR 013](docs/decisions/013-cost-per-pass-and-miss-log.md)). See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-205: Add independent code-review only where it provides value beyond verification; otherwise record its explicit deferral. Deferred: manual review found a missed compatibility regression, but the pilot did not compare a dedicated review skill against existing verification. Revisit when the [miss log](tests/behavior/misses.md) holds two or more defects that verification passed and review would have caught ([ADR 013](docs/decisions/013-cost-per-pass-and-miss-log.md)). See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-208: Test durable project-context refresh and task/session handoff against changed Git state and existing user instructions.

### Init, process rules and evaluation follow-ups

- [ ] KB-025 (moved from P0; blocks no release, see [ADR 012](docs/decisions/012-stable-release-gates.md)): Collect evidence from real use of the release. Criteria, baseline window, time box and reading rule fixed on 2026-11-08 in [real-use evidence](docs/real-use-evidence.md): M1 pair validity by `kaboost_audit_tdd.py --run`, M2 rework rate in aHerald against its history before the boundary, M3 interventions in the miss log; stop at 20 pairs or six weeks, fewer than 10 is inconclusive. Collecting since 2026-11-08: `tdd-commits` is enabled in aHerald (boundary `829e5c8`), watchdog and the private repository (local boundaries in the evidence document); the time box ends on 2026-12-20 or at 20 pairs. Remaining: at the end, write the M2 script on its own branch, mine both repositories and record the result in the [gate assessment](docs/release-gate-assessment.md).

- [ ] KB-238: Extend evaluation beyond single-session correctness (left open by KB-230): downstream measures (regressions after merge, handoff quality, reviewability), weaker or cheaper models, and multi-session tasks with handoff (KB-208). Deferred until the miss log or KB-025 shows where a process feature could pay off. The first calibration run after KB-234 checks that the judge's "minimal" score no longer differs between BASE and toolkit arms on the same task before its scores are used.

### Language modules

Decision 2026-10-30: language modules belong at project level, so KB-209 through KB-212 are delivered as per-stack packs of `/kaboost:init` (KB-221), offered and applied in the project rather than shipped as plugin-wide modules. Start them after the KB-219 to KB-221 practice base exists; each pack keeps the "opt-in" and "no global tooling mandate" requirements below.

- [ ] KB-211: Add an opt-in C++ module using the project's selected build system, compiler, and checks.
- [ ] KB-212: Verify language modules introduce no global tooling mandates or changes to unrelated projects.
- [ ] KB-213: Measure context and process overhead after each substantial content addition (the KB-222 core additions are the first case); simplify policies that fail the relevant gates. Static context is measured by `scripts/measure_context.py` with budgets and a record in [context overhead](docs/context-overhead.md) (2026-11-08: 1225 tokens always loaded). Open: process overhead against a no-toolkit baseline (needs model sessions under ADR 008) and the Codex skill-listing check.
- [ ] KB-245: Merge the `no-verify-guard` entry into existing `.claude/settings.json` and `.codex/hooks.json` (add and remove only the entry that names `kaboost_no_verify_guard.py`, keep the rest byte for byte, detect edits by hash). Deferred by [ADR 014](docs/decisions/014-opt-in-agent-hooks.md) point 5 until a user hits the conflict of an existing settings file.

**Done when:** the intended development workflow is covered without heavyweight procedures for routine changes, and optional modules preserve the language-agnostic core. Features without a demonstrated use case may be explicitly deferred with a reason.

## P3 — Expand native delivery and establish maintenance

### Additional adapters, selected by actual use

- [ ] KB-301: Revalidate current capabilities before implementing each adapter; record the native delivery choice and known incompatibilities.
- [ ] KB-302: Add Gemini CLI extension packaging and lifecycle tests when a consumer needs it.
- [ ] KB-303: Add Cursor native packaging, core-rule activation, and lifecycle tests when a consumer needs it.
- [ ] KB-304: Add Copilot CLI packaging and tests; name the exact supported Copilot surface.
- [ ] KB-305: Add OpenCode integration after selecting and documenting the supported version line.
- [ ] KB-306: Add Pi package integration and verify context-loading semantics.
- [ ] KB-307: For every implemented adapter, record tested client/OS versions, activation, precedence, limitations, and installation/update/rollback/removal commands.
- [ ] KB-308: Provide component selection through native mechanisms where practical; document bundle-only limitations.

### Ongoing quality and maintenance

- [ ] KB-309: Maintain shared behavior scenarios and client-specific regression evidence as supported clients evolve.
- [ ] KB-310: Define deprecation, migration, and release-maintenance procedures, including what triggers compatibility revalidation.
- [ ] KB-311: Document provenance and review requirements for optional third-party extensions; never auto-install them.
- [ ] KB-312: Reconcile README, roadmap, compatibility matrix, TODO, and DONE before every release.
**Done when:** every claimed adapter has tested delivery and behavior evidence, and maintenance procedures are documented. Unused integrations remain explicitly deferred; they do not block releases for the selected supported clients.

## Scope boundaries

- Full implementation means validated engineering content, workflows, and selected native adapters—not a universal plugin platform.
- Custom installers, package managers, sync engines, workstation bootstrap, dotfiles, and secrets synchronization remain out of scope.
- Hooks, agents, MCP integrations, and Jira connectors require a concrete use case and a separate scope decision; they are not implicit backlog commitments. Commands are in scope per [ADR 007](docs/decisions/007-explicit-commands.md); agent hooks only as opt-in project features of `init` per [ADR 014](docs/decisions/014-opt-in-agent-hooks.md).
- User Environment Sync remains an independent future project. Ordinary toolkit installation must not depend on it. See the [boundary](docs/sync-boundary.md).

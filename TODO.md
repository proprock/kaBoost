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

### Release and remote distribution

- [ ] KB-026 (decides KB-023/KB-025): Decide whether the stable release waits for KB-025. The documented release gates do not include improvement over baseline, and they are met or labeled; KB-025 has no recorded progress since rc.3 (no real red/green pairs, no defined metrics). Either publish v0.1.0 on the documented gates and move KB-025 to 0.2 as an evidence program, or keep the dependency and give KB-025 measurable criteria (red/green pairs passing `audit_tdd.py --run`, share of fix or revert commits touching the same files within N days, manual interventions), a baseline window, and a time box. Record the decision in the gate assessment.
- [ ] KB-027: Reassess the release gates for `v0.1.0-rc.3` (the assessment covers rc.2). Check whether the KB-217 cost data (skill-routing arm USD 0.129 against baseline USD 0.125 per session on `ah-queue-idle-gap`) can assess the Small-task token gate, which is currently unassessed; state why or why not.
- [ ] KB-025 (blocks KB-023): Collect evidence from real use of the release candidate. Use `v0.1.0-rc.N` in the maintainer's projects with the TDD red/green commit rule (KB-218); after about twenty red/green pairs (proposed; adjust), mine them and compare process compliance and rework with the earlier history, then record the result in the [gate assessment](docs/release-gate-assessment.md).
- [ ] KB-023: Publish v0.1.0 when authorized and all release gates are met, including the KB-025 evidence; verify installation from its published tag.

**Done when:** the published MVP is reproducibly installable, supported combinations have evidence, and the behavior pilot meets the [documented gates](docs/roadmap.md). Candidate publication enables remote checks; it does not establish stable-release readiness.

## P1 — Prove portability and strengthen lifecycle

### Remote distribution and platform evidence

- [ ] KB-112: Distribute the Codex adapter remotely (the Codex marketplace is local only) and verify install, update, rollback and removal from a published ref; run the Codex lifecycle on macOS and Windows. Record results in compatibility.
- [ ] KB-113: Verify the pinned remote Claude Code install on Linux and Windows, and repeat update and rollback between published refs for the current candidate (not repeated for rc.3).

**Done when:** two clients consume the same canonical engineering content through independently verified native mechanisms, with reproducible lifecycle procedures.

## P2 — Complete workflows and optional modules

### Engineering workflows

- [ ] KB-203: Add architecture-review for boundary, contract, migration, and high-risk design decisions. Deferred: the pilot did not demonstrate an architecture-boundary failure or the need for a separate skill beyond existing core and adaptive guidance. Revisit when a concrete high-risk design task exposes an uncovered gap, or when a matched behavior evaluation demonstrates added value; record the gap and independent evidence before adding it. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-204: Add a focused TDD skill with guidance for unit, integration, and contract testing and appropriate alternative checks. Deferred: the pilot found weak or missing tests, but did not establish that a separate skill improves on existing TDD and verification guidance. Revisit after a matched behavior evaluation measures independent test adequacy and Small-task overhead, or a concrete use case demonstrates an uncovered need. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-205: Add independent code-review only where it provides value beyond verification; otherwise record its explicit deferral. Deferred: manual review found a missed compatibility regression, but the pilot did not compare a dedicated review skill against existing verification. Revisit when a concrete review need exceeds verification or a matched evaluation shows additional defects found without disproportionate overhead. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-208: Test durable project-context refresh and task/session handoff against changed Git state and existing user instructions.

### Init, process rules and evaluation follow-ups

- [ ] KB-227: Make `/kaboost:init`, `/kaboost:init-global` and the Codex init skills work on Windows without `python3`. They call `python3` and `allowed-tools` permits only `Bash(python3 ...)`; on a machine without Store Python `python3` is the Store stub, while the README tells maintainers to use `py -3`. Add a fallback (`python3`, `python`, `py -3`) with matching permissions, and exercise the command path on Windows (the engine tests use `sys.executable`, so they do not cover it).
- [ ] KB-228: Move the TDD red/green commit rule (KB-218, ADR 011 "accepted for trial") out of the always-loaded core into an opt-in `init` feature until its benefit is measured, and ship `scripts/audit_tdd.py` with that feature. In the core it asks every project for two commits per change, a pushed red commit fails CI wherever the skip condition is missing (only `ci-python` carries it), and squash merges lose the pairs.
- [ ] KB-229: Exercise the interactive `/kaboost:init` and `/kaboost:init-global` flow (feature choice, preview, confirmation) end to end in Claude Code, and `$kaboost-init` in a live Codex session; KB-221, KB-223 and KB-224 closed without it.
- [ ] KB-230: Revise the ADR 008 decision rule. Requiring the pass-rate gain in points to reach the cost increase in percent caps any arm at (100 − baseline pass rate)% extra cost, so with the 20–80% calibration band and n = 10 almost no process feature can qualify; it also counts single-session correctness only. Consider cost per passing session alone, downstream measures (regressions after merge, handoff quality, reviewability), weaker or cheaper models, and multi-session tasks; replace the A/B-only revisit conditions of KB-203 to KB-205 with a log of real-use misses.
- [ ] KB-231: Allow prerelease versions (`0.1.0-rc.N`) in `scripts/validate.py` and the package manifests, so `claude plugin update` can move between candidates instead of uninstall and reinstall.
- [ ] KB-232: Maintainer decision on two AGENTS.md rules: branch naming per milestone (`feature/<milestone-name>`) does not match practice (`feature/<n>-<slug>` per pull request), and the ban on manual branch deletion leaves branches whose content reached master by other commits (`feature/23-calibration-harness`) undeletable by GitHub.
- [ ] KB-233: Record or retire the `claude plugin eval` assets (`evals/large-json-cli`, `tests/behavior/run_plugin_eval.py`); no task covers them, and `tests/behavior/test_plugin_eval_setup.py` is not run by CI.

### Language modules

Decision 2026-10-30: language modules belong at project level, so KB-209 through KB-212 are delivered as per-stack packs of `/kaboost:init` (KB-221), offered and applied in the project rather than shipped as plugin-wide modules. Start them after the KB-219 to KB-221 practice base exists; each pack keeps the "opt-in" and "no global tooling mandate" requirements below.

- [ ] KB-209: Add an opt-in Python module covering project-established uv, pytest, ruff, ty, and prek workflows. Mostly delivered by the init features `python-toolchain`, `make-checks`, `ci-python` and `precommit-hooks` (KB-221, KB-225); reconcile and keep only the remainder (for example the uv sandbox notes, practice 40).
- [ ] KB-210: Add an opt-in Rust module using the project's selected toolchain and checks. Demand exists: the KB-216 calibration tasks come from a Rust repository; include CI with the `TDD: red` skip condition.
- [ ] KB-211: Add an opt-in C++ module using the project's selected build system, compiler, and checks.
- [ ] KB-212: Verify language modules introduce no global tooling mandates or changes to unrelated projects.
- [ ] KB-213: Measure context and process overhead after each substantial content addition (the KB-222 core additions are the first case); simplify policies that fail the relevant gates. Static context is measured by `scripts/measure_context.py` with budgets and a record in [context overhead](docs/context-overhead.md) (2026-10-30: 1253 tokens always loaded). Open: process overhead against a no-toolkit baseline (needs model sessions under ADR 008) and the Codex skill-listing check.
- [ ] KB-226: Let `init` install agent hooks (Claude Code `settings.json` hooks, Codex hooks) on the user's confirmation, reversibly. Needs a decision that supersedes the hooks boundary in ADR 007 and a key-based managed-entry mechanism for JSON/TOML (no comments, so no begin/end markers): add and remove only kaBoost-owned entries, detect drift by hash, and keep the byte-exact restore acceptance of KB-221. Decide first which hooks are worth shipping (for example blocking `--no-verify`, the TDD red/green commit check from KB-218) and verify the current hook formats of both clients.

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
- [ ] KB-313: Add a scheduled (weekly) workflow that installs the latest Claude Code and Codex CLI and runs the disposable-profile lifecycle smoke tests, so client changes surface before a release; tested versions are fixed points (Claude Code 2.1.301–2.1.312, Codex CLI 0.165.0).
- [ ] KB-314: Pin GitHub Actions by commit SHA and review the `curl | bash` client installers in CI.
- [ ] KB-315: Make `scripts/validate.py` fail when compatibility, the gate assessment or the roadmap name an older release candidate than the current tag, so release facts cannot drift between manual reconciliations.

**Done when:** every claimed adapter has tested delivery and behavior evidence, and maintenance procedures are documented. Unused integrations remain explicitly deferred; they do not block releases for the selected supported clients.

## Scope boundaries

- Full implementation means validated engineering content, workflows, and selected native adapters—not a universal plugin platform.
- Custom installers, package managers, sync engines, workstation bootstrap, dotfiles, and secrets synchronization remain out of scope.
- Hooks, agents, MCP integrations, and Jira connectors require a concrete use case and a separate scope decision; they are not implicit backlog commitments. Commands are in scope per [ADR 007](docs/decisions/007-explicit-commands.md).
- User Environment Sync remains an independent future project. Ordinary toolkit installation must not depend on it. See the [boundary](docs/sync-boundary.md).

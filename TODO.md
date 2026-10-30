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

### Client loading and portability


### Behavior pilot


### Release and remote distribution

- [ ] KB-025 (blocks KB-023): Collect evidence from real use of the release candidate. Use `v0.1.0-rc.N` in the maintainer's projects with the TDD red/green commit rule (KB-218); after about twenty red/green pairs (proposed; adjust), mine them and compare process compliance and rework with the earlier history, then record the result in the [gate assessment](docs/release-gate-assessment.md).
- [ ] KB-023: Publish v0.1.0 when authorized and all release gates are met, including the KB-025 evidence; verify installation from its published tag.

**Done when:** the published MVP is reproducibly installable, supported combinations have evidence, and the behavior pilot meets the [documented gates](docs/roadmap.md). Candidate publication enables remote checks; it does not establish stable-release readiness.

## P1 — Prove portability and strengthen lifecycle


**Done when:** two clients consume the same canonical engineering content through independently verified native mechanisms, with reproducible lifecycle procedures.

## P2 — Complete workflows and optional modules

### Engineering workflows

- [ ] KB-203: Add architecture-review for boundary, contract, migration, and high-risk design decisions. Deferred: the pilot did not demonstrate an architecture-boundary failure or the need for a separate skill beyond existing core and adaptive guidance. Revisit when a concrete high-risk design task exposes an uncovered gap, or when a matched behavior evaluation demonstrates added value; record the gap and independent evidence before adding it. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-204: Add a focused TDD skill with guidance for unit, integration, and contract testing and appropriate alternative checks. Deferred: the pilot found weak or missing tests, but did not establish that a separate skill improves on existing TDD and verification guidance. Revisit after a matched behavior evaluation measures independent test adequacy and Small-task overhead, or a concrete use case demonstrates an uncovered need. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-205: Add independent code-review only where it provides value beyond verification; otherwise record its explicit deferral. Deferred: manual review found a missed compatibility regression, but the pilot did not compare a dedicated review skill against existing verification. Revisit when a concrete review need exceeds verification or a matched evaluation shows additional defects found without disproportionate overhead. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-208: Test durable project-context refresh and task/session handoff against changed Git state and existing user instructions.

### Language modules

KB-207 was closed on 2026-10-30 (routing verified, outcome benefit unproven), so these tasks are no longer frozen. Before starting KB-209 through KB-212, check them against the KB-219 to KB-221 practice base: `/kaboost:init` packs may replace them.

- [ ] KB-209: Add an opt-in Python module covering project-established uv, pytest, ruff, ty, and prek workflows.
- [ ] KB-210: Add an opt-in Rust module using the project's selected toolchain and checks.
- [ ] KB-211: Add an opt-in C++ module using the project's selected build system, compiler, and checks.
- [ ] KB-212: Verify language modules introduce no global tooling mandates or changes to unrelated projects.
- [ ] KB-219: Collect the practices found in the locally available projects (instruction files and rules, skills, hooks, settings, Makefile and CI checks, commit, branch and ticket conventions, test and documentation habits) and count in how many projects each same or similar practice appears. Private projects are reported only in aggregate, without names, paths, or code. Output: a table for the maintainer.
- [ ] KB-220: The maintainer picks from the KB-219 table by practical experience which practices were really useful. Store the picks as the feature base for `/kaboost:init`: for each feature a name, a short description, and the files or settings it adds or changes. Hooks need a scope decision first (ADR 007 keeps them out of scope).
- [ ] KB-221: Add `/kaboost:init`. When the user runs it in a project, it offers the features from the KB-220 base and shows what each would change. Features already applied in the project are shown as enabled and can be disabled. Each change is previewed and confirmed; user content is never overwritten (managed sections with markers).
- [ ] KB-218: Add a TDD commit rule to the core rules and adaptive workflow (check the 30–50 line core budget; evaluate before adopting per ADR 008): when work is test-driven, (1) write the tests, (2) commit the failing tests alone with the ticket ID and a message that marks them as tests (`KB-NNN: test: ...`, trailer `TDD: red`, naming the expected failing tests), (3) commit the solution as usual (trailer `TDD: green`). The split makes red/green pairs minable as fail-to-pass tasks for KB-216 and for process review; decide how CI treats red commits (check the PR head only; use `git bisect --first-parent`) and add an audit script that confirms the red commit fails and the green commit passes.
- [ ] KB-213: Measure context and process overhead after each substantial content addition; simplify policies that fail the relevant gates.

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
- Hooks, agents, MCP integrations, and Jira connectors require a concrete use case and a separate scope decision; they are not implicit backlog commitments. Commands are in scope per [ADR 007](docs/decisions/007-explicit-commands.md).
- User Environment Sync remains an independent future project. Ordinary toolkit installation must not depend on it. See the [boundary](docs/sync-boundary.md).

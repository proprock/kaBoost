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

- [ ] KB-018: Assess the release gates; label missing measurements as unassessed, fix demonstrated failures, and rerun affected scenarios.

### Release and remote distribution

- [ ] KB-019: Review release contents, source SHA, canonical/generated consistency, license, checksums, changelog, and accidental-secret checks.
- [ ] KB-020: Publish an explicitly identified release candidate when authorized; do not present an unpublished tag as installable.
- [ ] KB-021: Verify remote Git installation and tag pinning from a clean profile after candidate publication; test update and rollback between reviewed refs.
- [ ] KB-022: Finalize the tested client/OS support matrix, exact commands, limitations, and migration notes.
- [ ] KB-023: Publish v0.1.0 when authorized and all release gates are met; verify installation from its published tag.

**Done when:** the published MVP is reproducibly installable, supported combinations have evidence, and the behavior pilot meets the [documented gates](docs/roadmap.md). Candidate publication enables remote checks; it does not establish stable-release readiness.

## P1 — Prove portability and strengthen lifecycle


**Done when:** two clients consume the same canonical engineering content through independently verified native mechanisms, with reproducible lifecycle procedures.

## P2 — Complete workflows and optional modules

### Engineering workflows

- [ ] KB-203: Add architecture-review for boundary, contract, migration, and high-risk design decisions. Deferred: the pilot did not demonstrate an architecture-boundary failure or the need for a separate skill beyond existing core and adaptive guidance. Revisit when a concrete high-risk design task exposes an uncovered gap, or when a matched behavior evaluation demonstrates added value; record the gap and independent evidence before adding it. See [pilot workflow review](docs/pilot-workflow-review.md).
- [ ] KB-204: Add a focused TDD skill with guidance for unit, integration, and contract testing and appropriate alternative checks.
- [ ] KB-205: Add independent code-review only where it provides value beyond verification; otherwise record its explicit deferral.
- [ ] KB-206: Decide whether requirements-spec and task-workflow warrant separate skills; document merges or exclusions.
- [ ] KB-207: Verify Small/Medium/Large routing and Large-task readiness gates through behavior scenarios.
- [ ] KB-208: Test durable project-context refresh and task/session handoff against changed Git state and existing user instructions.

### Language modules

- [ ] KB-209: Add an opt-in Python module covering project-established uv, pytest, ruff, ty, and prek workflows.
- [ ] KB-210: Add an opt-in Rust module using the project's selected toolchain and checks.
- [ ] KB-211: Add an opt-in C++ module using the project's selected build system, compiler, and checks.
- [ ] KB-212: Verify language modules introduce no global tooling mandates or changes to unrelated projects.
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
- Hooks, agents, commands, MCP integrations, and Jira connectors require a concrete use case and a separate scope decision; they are not implicit backlog commitments.
- User Environment Sync remains an independent future project. Ordinary toolkit installation must not depend on it. See the [boundary](docs/sync-boundary.md).

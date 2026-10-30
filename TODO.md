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
- [ ] KB-207 (blocks KB-018 and KB-023; moved from P2): Verify Small/Medium/Large routing and Large-task readiness gates through behavior scenarios. The [first P2 trial](tests/behavior/kb207-results-2026-10-29.md) found no explicit workflow loading and missed readiness in all toolkit Large arms. A separate [loading diagnostic](tests/behavior/kb207-loading-diagnostic-2026-10-29.md) confirmed explicit loading; a [natural-routing probe](tests/behavior/kb207-natural-routing-2026-10-29.md) observed core markers but no toolkit skill or workflow invocation. A [before/after comparison](tests/behavior/kb207-routing-comparison-2026-10-29.md) did not observe improvement. A [60-session variant experiment](tests/behavior/kb207-routing-experiment-2026-10-29.md) led to [ADR 006](docs/decisions/006-planning-entry-point.md) (`plan-before-edit`): routing reached 10/10 on Large, but agents did not state the readiness items and independent acceptance still failed. A [holdout scenario](tests/behavior/kb207-holdout-2026-10-29.md) showed skill routing 10/10 and more verification, but an outcome ceiling (baseline also passed 10/10), no visible written gate, and 51% higher cost. A [harder rename holdout](tests/behavior/kb207-holdout-rename-2026-10-29.md) (baseline 8/10) showed no outcome benefit: the skill was invoked in 2/10 sessions and no written plan appeared. A `claude plugin eval` spike (3 runs per arm, scratch copy) showed `plan-before-edit` called first in 3/3 with the plugin from its description alone; the Δ was an artifact of an ordering grader. Cases now live in [evals/](evals/) and run through `tests/behavior/run_plugin_eval.py` (estimate first, then an explicit `--max-cost-usd`); outcome grading by the acceptance evaluators is not wired in because plugin eval has no command grader and the layout of kept workspaces is unverified. A [plan command measurement](tests/behavior/kb207-plan-command-2026-10-30.md) found that `/kaboost:plan` produced the full written gate in 10/10 sessions (skill routing alone 0/10), with no change in independent acceptance (0/30 on this task). Audit: all 30 Large sessions failed the same single check (the original `validate.py` ignores unknown arguments; every implementation made them exit 2), so the Large task cannot discriminate arms; [ADR 008](docs/decisions/008-evaluation-criteria.md) fixes the evaluation criteria and decision rule. A [calibration and A/B](tests/behavior/kb216-calibration-2026-10-30.md) on real fail-to-pass tasks found six of seven tasks at the baseline ceiling; on the one task in the 20–80% band `/kaboost:plan` passed 10/10 against 7/10 for baseline and skill routing at +74% cost per session, which does not meet the ADR 008 rule. With the rename task that is two calibrated tasks without demonstrated benefit. Remaining: the decision whether to close KB-207 under the ADR 008 stop rule or calibrate harder tasks first, then rerun matched, uninstrumented scenarios before claiming a pass.

### Release and remote distribution

- [ ] KB-019: Review release contents, source SHA, canonical/generated consistency, license, checksums, changelog, and accidental-secret checks.
- [ ] KB-021: Verify remote Git installation and tag pinning from a clean profile after candidate publication; test update and rollback between reviewed refs. Done so far: clean-profile install of the pinned `v0.1.0-rc.2` through `proprock/marketplace` (with commands present). Remaining: update and rollback between two reviewed refs.
- [ ] KB-022: Finalize the tested client/OS support matrix, exact commands, limitations, and migration notes.
- [ ] KB-023: Publish v0.1.0 when authorized and all release gates are met; verify installation from its published tag.

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

Frozen until KB-207 is resolved: do not start KB-209 through KB-212 while natural skill routing is unverified.

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

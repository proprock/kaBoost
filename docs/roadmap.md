# Roadmap and readiness

This document defines milestones and release gates. [TODO.md](../TODO.md) is the operational checklist; [DONE.md](../DONE.md) records completed work. Move finished tasks or entire completed sections from TODO to DONE with completion dates and verification evidence. Keep partially completed sections in TODO with only their unfinished tasks, and avoid duplicate entries.

## 0.1 candidate — one client, four skills

Deliver English documentation/ADRs, 30–50-line core, plan-before-edit/project-context/debugging/verification, Claude local/Git marketplace metadata, deterministic build, inventory, lifecycle smoke harness, and cross-platform package CI. No hooks, MCP, installer, registry, Jira connector, or runtime dependencies.

Candidate readiness: canonical/generated validation and packaging tests pass; native Claude strict validation and isolated local lifecycle pass; user-owned files remain intact. Record untested platforms honestly.

## Pilot and release gate

Use an existing project and frozen initial commits for Small/Medium/Large changes. Run three paired baseline/toolkit trials per task using the same model/client, permissions, check commands, and budget. Baseline retains the project's normal instructions. Toolkit arm adds core and the plugin. Use isolated worktrees/profiles, alternate arm order, and keep raw evidence local without secrets. Do not let one trial's solution leak into another.

Record AC pass/fail, test adequacy, unrelated diff, architecture violations, manual interventions, input/output tokens (when available), and wall time. Use independent acceptance checks. Define the complex task's readiness gate before running it.

Release gate: no critical requirement/security/boundary violation; quality no worse than baseline; proposed Small-task median time/token overhead <=20%. If tokens cannot be measured, mark that gate unassessed, not passed. Three tasks are a pilot, not statistical proof. See tests/behavior for scenarios and recording format.

Tag v0.1.0 only after checking the release inventory, changelog, source SHA, license, secret scan, native loading, and pending evidence. Publication/push is a separate authorized action. Remote install cannot be claimed before publication. Do not fabricate pilot results.

## Next

1. Verify remote distribution for the existing Codex adapter after reviewed publication.
2. Complete outstanding native lifecycle and core-loading checks by client and OS; document a supported version range only after tests.
3. Add architecture review, requirements/task references, or TDD skills only when pilot tasks expose a gap.
4. Add language-specific Python/Rust/C++ modules without imposing their tools globally.
5. Add Gemini/Cursor/Copilot/OpenCode/Pi adapters by practical demand, not for matrix completeness.

Automatic sync, universal plugin frameworks, package managers, and workstation provisioning remain out of scope.

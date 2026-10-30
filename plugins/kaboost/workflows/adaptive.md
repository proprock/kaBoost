# Adaptive task workflow

Choose depth by risk and uncertainty, not file count. Escalate when new evidence increases risk; do not require documents for trivial work.

| Level | Trigger | Required outcome |
| --- | --- | --- |
| Small | Clear local change without material contract or security impact | Brief acceptance criteria, focused change, relevant verification |
| Medium | Multiple related parts or ambiguous behavior without high-risk boundary changes | Compact requirements and plan, verified incremental changes |
| Large | Public API/schema migration, security/concurrency risk, changed architecture boundaries, or substantial uncertainty | Requirements, decision record, decomposition, readiness check, implementation and review |

For Medium, state why, scope, constraints, non-goals, and acceptance criteria in the conversation or existing ticket. For Large, also compare viable designs, identify compatibility/rollback needs, and record the selected tradeoff in an ADR. Readiness means acceptance criteria are testable, dependencies and contracts are understood, and material unknowns have an owner or experiment.

## Requirements reference

For a ticket or request, identify the outcome, scope, non-goals, constraints, and observable acceptance criteria in the existing task record or conversation. Match detail to risk; do not create a specification for a straightforward edit. Separate missing facts from assumptions, resolve material ambiguity with the available evidence, and ask only when it blocks a consequential choice.

For changes to behavior or public boundaries, inspect relevant callers, documentation, tests, and existing behavior before defining compatibility criteria. Include success, failure, and unchanged behavior where applicable; do not assume a general instruction to preserve compatibility identifies every contract. Map each criterion to an independent check or inspection, and record any contract or check that remains uncertain.

## Task workflow reference

- Use the project's ticket and branch conventions. Inspect the current branch and working tree before creating a feature branch; preserve user changes and choose the base using the project's workflow.
- Keep commits focused and use Conventional Commits unless local conventions differ; include a task identifier when the project requires it. Commit, push, or change external systems, including ticket updates, only with the applicable authorization.
- When preparing a PR, describe the problem, resulting behavior, relevant checks, and remaining limitations. Compare the actual diff with the intended base and acceptance criteria; do not imply that unrun checks passed. Open or publish the PR only when authorized.
- At handoff, record the task or ticket, acceptance criteria and scope, branch/base, working-tree state, verified evidence, unresolved issues, and next action. Reuse the existing task record and omit secrets and unnecessary artifacts.

TDD is preferred for deterministic behavioral changes and reproducible regressions: observe the expected failure, implement the smallest correction, then refactor with checks passing. Record the cycle in two commits: first the failing tests alone, with the task ID, a message that marks them as tests, the trailer `TDD: red`, and an `Expected failing:` line naming the tests; then the solution with the trailer `TDD: green`. Push both together or judge CI on the pull-request head, because a red commit fails by design; the pair can be checked with `scripts/audit_tdd.py` and found again with `git bisect --first-parent`. Skip the split for documentation, exploratory work, and configuration. For documentation, exploratory work, or configuration, use a relevant alternative check. Choose unit tests for isolated behavior, integration tests for collaborating components, and contract tests for public boundaries.

# Adaptive task workflow

Choose depth by risk and uncertainty, not file count. Escalate when new evidence increases risk; do not require documents for trivial work.

| Level | Trigger | Required outcome |
| --- | --- | --- |
| Small | Clear local change without material contract or security impact | Brief acceptance criteria, focused change, relevant verification |
| Medium | Multiple related parts or ambiguous behavior without high-risk boundary changes | Compact requirements and plan, verified incremental changes |
| Large | Public API/schema migration, security/concurrency risk, changed architecture boundaries, or substantial uncertainty | Requirements, decision record, decomposition, readiness check, implementation and review |

For Medium, state why, scope, constraints, non-goals, and acceptance criteria in the conversation or existing ticket. For Large, also compare viable designs, identify compatibility/rollback needs, and record the selected tradeoff in an ADR. Readiness means acceptance criteria are testable, dependencies and contracts are understood, and material unknowns have an owner or experiment.

Use the project's ticket and branch conventions. Inspect the working tree before creating a feature branch; preserve user changes. Use Conventional Commits unless local conventions differ. Prepare a focused PR description with behavior and validation when requested. Publishing and external ticket updates require task authorization.

TDD is preferred for deterministic behavioral changes and reproducible regressions: observe the expected failure, implement the smallest correction, then refactor with checks passing. For documentation, exploratory work, or configuration, use a relevant alternative check. Choose unit tests for isolated behavior, integration tests for collaborating components, and contract tests for public boundaries.

At a session boundary, hand off the goal, AC, branch/base, working-tree state, evidence, unresolved issues, and next step. Reuse the existing task record. Avoid intermediate artifacts with no downstream consumer.

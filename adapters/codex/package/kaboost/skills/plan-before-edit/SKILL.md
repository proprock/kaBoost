---
name: plan-before-edit
description: Use BEFORE the first edit when a task adds or changes a CLI flag, output format, public API, schema, config, security behavior, or anything callers or users may depend on, or when scope is unclear. Finds existing contracts and states criteria, non-goals and alternatives before code changes.
---
# Plan before edit

1. Find what already depends on the thing you will change: callers, tests, docs, and current behavior for default and invalid inputs. Run or read the existing code to confirm.
2. Before the first edit, state briefly: acceptance criteria, non-goals, existing behavior that must stay unchanged, one alternative design and why it was rejected, and the checks you will run (success, failure, compatibility).
3. Then implement in small verified steps and run the checks. Escalate if new evidence raises the risk.

Skip only for typo, documentation, or one-line local fixes.

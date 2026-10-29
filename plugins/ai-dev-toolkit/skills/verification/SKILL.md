---
name: verification
description: Verify a substantive implementation against acceptance criteria before reporting completion, or audit an explicit completion claim. Use lightweight checks for documentation-only edits.
---
# Verification

Start with the task's acceptance criteria and affected contracts. Map each criterion to evidence: a behavior test, integration/contract check, static check, or focused inspection. Use established project commands and the smallest sufficient checks; do not invent an exhaustive test matrix for a local edit.

Inspect the actual final diff and Git state. Check scope, user changes, architecture boundaries, compatibility, error paths, and accidental secrets. Confirm tests exercise the intended behavior rather than mirror implementation details. Read failures before deciding whether they are pre-existing; reproduce or compare with a baseline when safe.

Run the relevant checks after the final code change. Record commands, outcomes, and material environment limits. Label skipped, unavailable, or failed checks explicitly. Do not claim CI, another OS, deployed state, or live integration was verified from repository inspection alone.

For a remaining failure, identify the unmet criterion and next action. Report partial completion honestly. Never edit tests or disable checks just to obtain a passing result.

Deliver a compact result: what changed and why, criteria covered, checks and outcomes, and unresolved risks. Do not create a verification document unless requested or useful for a required handoff.

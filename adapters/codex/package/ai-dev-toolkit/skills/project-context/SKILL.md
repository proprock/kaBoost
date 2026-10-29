---
name: project-context
description: Inspect or refresh repository context when onboarding, resuming stale work, or preparing a session handoff. Also use before implementation when a task involves substantial uncertainty, public contract changes, architecture, security, or migrations and needs proportional planning. Skip routine low-risk edits in a known repository.
---
# Project context

For a task involving substantial uncertainty or changes to public contracts, architecture, security, or migrations, first read and follow [the adaptive workflow](../../workflows/adaptive.md). State the Large-task readiness items before source or test edits when applicable. Do not create context files unless authorized.

Read existing instructions and context before proposing another document. Use the project's preferred code-discovery tools. Inspect manifests, CI, relevant entrypoints, boundaries, and Git state; report observations separately from unverified claims. Do not execute unfamiliar bootstrap scripts just to discover commands.

For durable context, capture only stack, canonical check commands, architecture boundaries, local conventions, and important decisions. Link to maintained sources instead of copying their contents. Record the inspected commit and any unavailable checks. Existing documentation takes precedence over a new toolkit template.

For task/session context, capture ticket or goal, acceptance criteria, scope/non-goals, branch and base commit, working-tree changes, verified findings, check results, unresolved questions, and next action. Keep this separate from durable project facts. Never include secrets or full session transcripts.

On resume, compare the recorded commit, branch, and working tree with current state. Recheck affected claims rather than treating old context as authoritative.

Return concise findings in the conversation by default. Create or modify context files only when authorized; ask before changing user-owned instruction files. Do not generate parallel AGENTS.md, CLAUDE.md, and context documents with the same content.

For routine context lookup, do not load the adaptive workflow unless requirements or proportional planning are needed.

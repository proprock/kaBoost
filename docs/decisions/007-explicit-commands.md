# 007: Explicit commands

Status: accepted

## Decision

Add user-invoked Claude Code commands next to the skills: `/kaboost:plan`, `/kaboost:debug`, `/kaboost:verify`, `/kaboost:context`, and `/kaboost:help`. Each command names one skill and passes its arguments. `/kaboost:plan` also fixes the reply format that must appear before the first edit: criteria, non-goals, must-not-change, rejected alternative, checks. Commands set `disable-model-invocation`, so they add no description to the model's skill listing. No `kaboost-help` skill is added for the same reason.

## Evidence

[ADR 006](006-planning-entry-point.md) fixed skill routing (10/10 in the variant experiment) but agents still did not state the readiness items, and independent acceptance of the Large task failed. A command makes the choice explicit and lets the reply format be checked mechanically. OpenSpec and BMAD both use explicit entry points (`/opsx:propose`, `bmad-help`) rather than relying on automatic routing; neither relies on hooks as far as the public documentation shows.

## Alternatives and tradeoffs

- **Hooks (`UserPromptSubmit`, `PreToolUse`):** deterministic, but they run code on the user's machine and stay out of scope until commands are shown insufficient.
- **Description routing only:** keeps the surface smaller, but leaves the missing written gate unaddressed.
- **A help skill:** one more description in every session's listing; the command costs nothing until used.

## Consequences

- Supersedes the scope boundary that listed commands as needing a separate decision. Hooks, agents, MCP integrations, and Jira connectors remain out of scope.
- Commands are not generated for Codex; its package keeps skills only.
- Whether the `/kaboost:plan` format improves gate compliance is unmeasured (KB-215).

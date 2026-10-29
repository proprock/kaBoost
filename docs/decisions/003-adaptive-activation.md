# 003: Adaptive activation

Status: accepted

## Decision

Keep only invariants always active; ship three focused skills and an on-demand adaptive reference.

## Alternatives and tradeoffs

A complete mandatory framework increases overhead. A single giant skill loads unrelated procedures.

## Consequences

Skill routing is probabilistic; explicit invocation and behavior evaluations are necessary. TDD depth follows behavior and risk.

## Routing revision under evaluation — 2026-10-29

The KB-207 [natural-routing probe](../../tests/behavior/kb207-natural-routing-2026-10-29.md) observed core loading but no toolkit skill or adaptive workflow invocation. Core now names `project-context` as the entry point for higher-risk work, and that skill's description and first instruction cover those triggers. Routine low-risk edits remain excluded. This is a candidate change, not evidence of improved behavior; compare with the previous toolkit in matched uninstrumented trials and measure Small overhead before claiming success.

The [BMAD skills reference](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs/reference/skills-and-agents.md) documents explicit workflow skills and a guidance hub; its [build skill](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/bmad-build/SKILL.md) describes both applicable tasks and exclusions. The local change borrows the idea of a discoverable entry point with clear triggers, without adopting BMAD's agents, installer, rendering runtime, or wording. BMAD's explicit invocation design does not demonstrate automatic routing reliability for this toolkit.

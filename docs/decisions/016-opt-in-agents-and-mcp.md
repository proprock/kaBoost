# 016: Opt-in agent definitions and MCP server entries through init

Status: proposed (2026-11-20, KB-253). No code, catalog or scope-boundary text changes until the maintainer accepts this record.

## Context

The scope boundary in [TODO.md](../../TODO.md#scope-boundaries) keeps agents and MCP integrations out unless a concrete use case and a separate decision exist. [ADR 014](014-opt-in-agent-hooks.md) lifted the same boundary for hooks, and the hook (`no-verify-guard`) gave the only measured compliance result so far. Two gaps point at agents and MCP:

- An independent review needs its own context. A skill runs in the agent's context and sees its reasoning; a subagent does not (KB-205 waits for evidence that such a review catches what verification misses).
- The global features `code-discovery` and `context7` tell the agent to use tools that `init` cannot set up, so a repository can carry the rule without the server.

## Client facts

Checked on 2026-11-20 with Context7 against the vendors' documentation; installed clients: Claude Code 2.1.325, codex-cli 0.169.0. Verify both again against the installed clients before implementing, as ADR 014 did.

- **Claude Code agents:** project subagents are Markdown files with YAML frontmatter (`name`, `description`, optional `tools`, `model`, `mcpServers`) under `.claude/agents/`; the body is the system prompt. A subagent may declare MCP servers inline, connected only while it runs. The documentation consulted describes no approval step for project agents beyond trusting the workspace. Source: [sub-agents](https://code.claude.com/docs/en/sub-agents).
- **Claude Code MCP:** project servers live in `.mcp.json` at the repository root (`{"mcpServers": {...}}`), meant to be checked in. Claude Code asks for approval before it uses a server from `.mcp.json`; `enableAllProjectMcpServers` approves all, and `claude mcp reset-project-choices` resets the choice. Sources: [MCP scopes](https://code.claude.com/docs/en/mcp), [settings](https://code.claude.com/docs/en/settings).
- **Codex agents:** custom agents are standalone TOML files under `.codex/agents/` (project) or `~/.codex/agents/` (personal) with required `name`, `description` and `developer_instructions`; they inherit the parent's permissions, provider and MCP servers and cannot override them. Source: [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- **Codex MCP:** project servers go into `.codex/config.toml` (`[mcp_servers.<name>]`). Codex loads every project `.codex/` layer, including that file, hooks and rules, only when the user trusts the project; `codex exec` loads project MCP servers only for trusted projects, and they can run commands outside the sandbox. Sources: [advanced config](https://learn.chatgpt.com/docs/config-file/config-advanced), [MCP](https://learn.chatgpt.com/docs/llms-full.txt).

## Proposed decision

Shaped like ADR 014:

1. Agent definitions and MCP server entries may be shipped only as opt-in `init` features: offered, previewed in full, written after confirmation, removed by `disable`. The plugin and Codex package manifests declare no agents and no MCP servers, so installing kaBoost still starts nothing.
2. Project scope only, where the team reviews the files. No global agent and no global MCP entry.
3. An agent definition is a file kaBoost owns (`.claude/agents/kaboost-<name>.md`, `.codex/agents/kaboost-<name>.toml`), so the existing hash-based drift detection covers it; the Claude file keeps its YAML header above the begin marker, as `init` skill files already do. The Codex TOML file can carry the markers as `#` comments, which TOML allows; whether to use `own` with comment markers or `exact` is settled at implementation after checking that Codex loads such a file.
4. An MCP entry follows ADR 014 point 5: the engine creates `.mcp.json` or `.codex/config.toml` only when it does not exist, deletes it on `disable`, and otherwise reports a conflict with the entry to add by hand. Merging into an existing file waits for the same demand as KB-245.
5. The preview says what the client asks before it uses the entry: Claude Code's approval of project MCP servers, and Codex's project trust for both agents and MCP.

## First candidates and their evidence

- **Agent:** a read-only reviewer (`tools` limited to reading and searching; Codex: `sandbox_mode = "read-only"` where the client supports it) that reviews a diff against the task's acceptance criteria. Trigger: two entries in the [miss log](../../tests/behavior/misses.md) of defects that verification passed and a review would have caught, the same trigger as KB-205 under [ADR 013](013-cost-per-pass-and-miss-log.md).
- **MCP entry:** a project entry for a documentation server, offered together with the `context7` rules. Trigger: a repository that enables the `context7` rules while no documentation server or CLI is available to the agent there, recorded as a miss.

Neither candidate is built before its trigger.

## Alternatives and tradeoffs

- **Keep the boundary.** Nothing new runs, but the review gap stays a skill in the same context, and rules keep naming tools the repository does not configure.
- **Agents and MCP servers in the plugin manifest.** Simplest to ship, but always on for everyone who installs kaBoost and outside the project's review; MCP servers start processes. That breaks opt-in, as ADR 014 found for hooks.
- **Global configuration.** Covers every repository at once, but changes projects the user did not choose, against the "no global mandate" requirement.

## Consequences if accepted

- Amends the scope-boundary sentence in TODO.md and the agents part of ADR 007 and ADR 009, as ADR 014 did for hooks; Jira connectors stay out of scope.
- An MCP entry runs a process on the user's machine whenever the client starts with the project trusted and approved; the preview must show the full command, and the entry must pin the server's version.
- Implementation tasks are created only when a trigger above is met; KB-253 closes with the decision.

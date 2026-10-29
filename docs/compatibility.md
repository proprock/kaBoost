# Compatibility and evidence

Documentation reviewed 2026-10-29. “Documented” is not “runtime tested.” No universal plugin or instruction-precedence semantics are claimed.

| Client | Instruction surface | Delivery and update | Toolkit status |
| --- | --- | --- | --- |
| Claude Code | ~/.claude/CLAUDE.md, project CLAUDE.md/rules; imports compose context | .claude-plugin/plugin.json, custom Git/local marketplace; native update/uninstall | MVP; exact local evidence below |
| Codex | $CODEX_HOME/AGENTS.md, project hierarchy; closer rules specialize | Agent Skills, .codex-plugin/plugin.json; documented local marketplace | Researched; no adapter/runtime claim |
| Gemini CLI | ~/.gemini/GEMINI.md and hierarchical project context | gemini-extension.json; Git/local install, --ref, update/uninstall; gallery | Researched; no adapter |
| Cursor | User Rules settings, project rules/AGENTS.md | Cursor plugins and Agent Plugins; GitHub marketplace import; native management | Researched; no adapter |
| Copilot CLI | ~/.copilot/copilot-instructions.md, repository/path instructions | Git/URL/local custom marketplace, native plugins/update | Researched; no adapter; not a claim about every Copilot surface |
| OpenCode | Global/project AGENTS.md | Agent Skills; executable plugins are a separate mechanism | Researched; no marketplace parity claim; v1/v2 docs differ |
| Pi | Native agent context; exact precedence deferred to adapter | Agent Skills, Git/npm/local Pi packages | Researched; no adapter |

Claude, Gemini, Cursor native plugins support combinations of skills, commands, agents, hooks, and MCP. Their formats and execution semantics differ. Pi extensions are a different interface; MCP/subagents must not be assumed built in. None of these facilities is a runtime requirement of this toolkit. Codex remote custom marketplace parity is not inferred from desktop local catalogs.

Codex's file hierarchy is documented; Claude and Gemini compose multiple instruction sources. Copilot CLI explicitly does not define a general precedence between applicable instruction files. Therefore avoid conflicting content instead of imposing a cross-client last-wins model.

## Runtime evidence

| Check | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Python package checks | Hosted CI passed, Python 3.10/3.13 | Hosted CI passed, Python 3.10/3.13 | Hosted CI passed, Python 3.10/3.13 |
| Claude 2.1.301 strict metadata validation | See validation record | Pending | Pending |
| Isolated local marketplace lifecycle | See validation record | Pending | Claude 2.1.312 passed on Windows Server 2025; see validation record |
| Authenticated model skill discovery / explicit invocation | Passed with profile caveat; see validation record | Pending | Pending |
| Behavior pilot | Pending | Pending | Pending |
| Remote tagged marketplace install | Pending publication | Pending publication | Pending publication |

[Validation record](validation.md) records actual commands. Minimum supported Claude version remains unestablished; 2.1.301 is a tested point, not a minimum-version promise. Portable files use LF and ordinary copies without Unix symlinks or shell scripts. OS portability still requires native runtime tests.

## Primary sources

- [Claude marketplace](https://code.claude.com/docs/en/plugin-marketplaces), [install](https://code.claude.com/docs/en/plugins/install), [memory](https://code.claude.com/docs/en/memory).
- [Codex packaging](https://developers.openai.com/plugins/build/plugins), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- [Gemini extensions](https://geminicli.com/docs/extensions/reference/), [context](https://geminicli.com/docs/cli/gemini-md/).
- [Cursor plugins](https://cursor.com/docs/plugins), [skills and GitHub import](https://cursor.com/docs/skills).
- [Copilot CLI plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [instruction precedence](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
- [OpenCode rules](https://opencode.ai/docs/rules/), [v2 skills](https://opencode.ai/v2/docs/skills).
- [Pi packages](https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/packages.md).

Recheck sources when adding an adapter. Record the client version, OS, scope, install/update/remove commands, loaded components, core attachment, and known incompatibilities.

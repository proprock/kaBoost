# Compatibility and evidence

Documentation reviewed 2026-10-29. “Documented” is not “runtime tested.” No universal plugin or instruction-precedence semantics are claimed.

| Client | Instruction surface | Delivery and update | Toolkit status |
| --- | --- | --- | --- |
| Claude Code | ~/.claude/CLAUDE.md, project CLAUDE.md/rules; imports compose context | .claude-plugin/plugin.json, custom Git/local marketplace; native update/uninstall | MVP; exact local evidence below |
| Codex CLI | $CODEX_HOME/AGENTS.md, project hierarchy; closer rules specialize | Agent Skills, .codex-plugin/plugin.json; local marketplace | Unreleased adapter; exact local evidence below |
| Gemini CLI | ~/.gemini/GEMINI.md and hierarchical project context | gemini-extension.json; Git/local install, --ref, update/uninstall; gallery | Researched; no adapter |
| Cursor | User Rules settings, project rules/AGENTS.md | Cursor plugins and Agent Plugins; GitHub marketplace import; native management | Researched; no adapter |
| Copilot CLI | ~/.copilot/copilot-instructions.md, repository/path instructions | Git/URL/local custom marketplace, native plugins/update | Researched; no adapter; not a claim about every Copilot surface |
| OpenCode | Global/project AGENTS.md | Agent Skills; executable plugins are a separate mechanism | Researched; no marketplace parity claim; v1/v2 docs differ |
| Pi | Native agent context; exact precedence deferred to adapter | Agent Skills, Git/npm/local Pi packages | Researched; no adapter |

Claude, Gemini, Cursor native plugins support combinations of skills, commands, agents, hooks, and MCP. Their formats and execution semantics differ. Pi extensions are a different interface; MCP/subagents must not be assumed built in. None of these facilities is a runtime requirement of this toolkit. Codex CLI documents remote Git marketplace sources; parity across all IDE and desktop surfaces is not established.

Codex's file hierarchy is documented; Claude and Gemini compose multiple instruction sources. Copilot CLI explicitly does not define a general precedence between applicable instruction files. Therefore avoid conflicting content instead of imposing a cross-client last-wins model. The [Codex research record](codex-research.md) distinguishes CLI, IDE, desktop, and remote marketplace documentation from runtime evidence.

## Runtime evidence

| Check | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Python package checks | Hosted CI passed, Python 3.10/3.13 | Hosted CI passed, Python 3.10/3.13 | Hosted CI passed, Python 3.10/3.13 |
| Claude 2.1.301 strict metadata validation | See validation record | Pending | Pending |
| Claude isolated local marketplace lifecycle | Claude 2.1.301 and 2.1.312 passed; see validation record | Claude 2.1.312 passed on macOS 26.6.2 | Claude 2.1.312 passed on Windows Server 2025 |
| Codex CLI isolated local marketplace lifecycle | 0.165.0 passed; see adapter guide | Pending | Pending |
| Authenticated skill discovery / explicit invocation | Claude 2.1.312 and Codex CLI 0.165.0 passed with profile caveats; see records | Pending | Pending |
| Behavior pilot | Claude and Codex trials recorded; release gate not met | Pending | Pending |
| Remote tagged marketplace install | Pending publication | Pending publication | Pending publication |

[Validation record](validation.md), [Codex adapter guide](../adapters/codex/README.md), and [comparison results](../tests/behavior/codex-comparison-results-2026-10-29.md) record scope and limitations. Portable files use LF and ordinary copies without Unix symlinks or shell scripts. OS portability still requires native runtime tests.

## Client version and revalidation policy

The unreleased toolkit has **no established supported version range or minimum**. The table records tested points only: Claude Code 2.1.301 and 2.1.312 and Codex CLI 0.165.0. A passed lifecycle does not imply authenticated loading, instruction behavior, remote distribution, or release readiness. Other versions and client surfaces are unverified until evidence is recorded; patch releases are not automatically assumed compatible. A release must identify its exact tested toolkit commit, client versions, OS, and check scope before claiming support.

Review the client vendor's current primary documentation and release notes before adding a client, changing a tested client version, or preparing a release. Compare native manifest and catalog fields, installation/update/removal commands, skill discovery and instruction loading against the adapter and documented limitations. Record sources, date, version, affected surfaces, and any changed assumptions; a documentation review alone is not runtime evidence.

Repeat the relevant checks when the client version, OS, native package or catalog format, canonical skill metadata, installation procedure, or instruction activation changes; also repeat them after an observed regression or a vendor-announced breaking change. Run both package builders in check mode, both adapter validations, packaging tests, and the affected client's disposable-profile lifecycle harness. For changes to discovery or instruction semantics, additionally repeat authenticated discovery, explicit invocation and the affected core/precedence scenario; record profile caveats. Repeat remote install and rollback checks only when reviewed published refs are available, and rerun affected behavior scenarios when model-facing content or routing changes. A new OS or surface needs its own native evidence, not extrapolation.

Record commands, source commit, client and model versions where applicable, OS, results and limitations. A failed, unavailable or unrun check is not a pass: leave that combination unverified, investigate the failure and update documentation before making a support claim. CI configuration or an old successful run does not prove that a new commit or version passed. The release gate in [roadmap](roadmap.md) remains separate from compatibility checks.

## Primary sources

- [Claude marketplace](https://code.claude.com/docs/en/plugin-marketplaces), [install](https://code.claude.com/docs/en/plugins/install), [memory](https://code.claude.com/docs/en/memory).
- [Codex packaging](https://developers.openai.com/plugins/build/plugins), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- [Gemini extensions](https://geminicli.com/docs/extensions/reference/), [context](https://geminicli.com/docs/cli/gemini-md/).
- [Cursor plugins](https://cursor.com/docs/plugins), [skills and GitHub import](https://cursor.com/docs/skills).
- [Copilot CLI plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [instruction precedence](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
- [OpenCode rules](https://opencode.ai/docs/rules/), [v2 skills](https://opencode.ai/v2/docs/skills).
- [Pi packages](https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/packages.md).

Recheck sources when adding an adapter. Record the client version, OS, scope, install/update/remove commands, loaded components, core attachment, and known incompatibilities.

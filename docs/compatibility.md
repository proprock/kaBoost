# Compatibility and evidence

Documentation reviewed 2026-10-30. “Documented” is not “runtime tested.” No universal plugin or instruction-precedence semantics are claimed.

| Client | Instruction surface | Delivery and update | Toolkit status |
| --- | --- | --- | --- |
| Claude Code | ~/.claude/CLAUDE.md, project CLAUDE.md/rules; imports compose context | .claude-plugin/plugin.json, custom Git/local marketplace; native update/uninstall | Release `v0.2.0`: skills and commands of `v0.1.0`, core without the TDD red/green commit rule, extended init features; exact evidence below |
| Codex CLI | $CODEX_HOME/AGENTS.md, project hierarchy; closer rules specialize | Agent Skills, .codex-plugin/plugin.json; Git marketplace (`proprock/marketplace`) or local | Released adapter in `proprock/marketplace`, pinned `v0.2.0` (skills only, no commands); exact evidence below |
| Gemini CLI | ~/.gemini/GEMINI.md and hierarchical project context | gemini-extension.json; Git/local install, --ref, update/uninstall; gallery | Researched; no adapter |
| Cursor | User Rules settings, project rules/AGENTS.md | Cursor plugins and Agent Plugins; GitHub marketplace import; native management | Researched; no adapter |
| Copilot CLI | ~/.copilot/copilot-instructions.md, repository/path instructions | Git/URL/local custom marketplace, native plugins/update | Researched; no adapter; not a claim about every Copilot surface |
| OpenCode | Global/project AGENTS.md | Agent Skills; executable plugins are a separate mechanism | Researched; no marketplace parity claim; v1/v2 docs differ |
| Pi | Native agent context; exact precedence deferred to adapter | Agent Skills, Git/npm/local Pi packages | Researched; no adapter |

Claude, Gemini, Cursor native plugins support combinations of skills, commands, agents, hooks, and MCP. Their formats and execution semantics differ. Pi extensions are a different interface; MCP/subagents must not be assumed built in. None of these facilities is a runtime requirement of this toolkit. Codex CLI documents remote Git marketplace sources; parity across all IDE and desktop surfaces is not established.

Codex's file hierarchy is documented; Claude and Gemini compose multiple instruction sources. Copilot CLI explicitly does not define a general precedence between applicable instruction files. Therefore avoid conflicting content instead of imposing a cross-client last-wins model. The [Codex research record](codex-research.md) distinguishes CLI, IDE, desktop, and remote marketplace documentation from runtime evidence.

## Runtime evidence

The table is a summary: the newest tested client version and the result per cell. The dated lists below it hold the detail, newest first, as `date — OS — client version — toolkit ref — what was checked — result (task ID)`. Add a new result as a list entry and update the cell; do not grow the cell.

| Check | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Python package checks | Passed (CI, Python 3.10/3.13) | Passed (CI, Python 3.10/3.13) | Passed (CI, Python 3.10/3.13) |
| Claude strict metadata validation | 2.1.301 passed | Pending | Pending |
| Claude isolated local marketplace lifecycle | 2.1.312 passed | 2.1.312 passed | 2.1.312 passed |
| Codex CLI isolated local marketplace lifecycle | 0.165.0 passed | Pending | 0.167.0 passed |
| Codex CLI remote lifecycle between pinned Git tags (`scripts/smoke_codex_remote.py`) | Pending | Pending | 0.167.0 passed |
| Authenticated skill discovery / explicit invocation | Claude 2.1.312, Codex 0.165.0 passed with caveats | Pending | Pending |
| Behavior pilot | Recorded; see the [gate assessment](release-gate-assessment.md) | Pending | Pending |
| Remote tagged marketplace install (`proprock/marketplace`) | Claude 2.1.319 passed (`v0.1.1`) | Claude 2.1.308 passed (rc.3) | Claude 2.1.319 passed (`v0.2.0`) |
| Update and rollback between two pinned Git tags | Claude 2.1.319 passed | Claude 2.1.308 passed (fixture tags) | Claude 2.1.319 passed |
| Release artifacts reproducible and complete | Passed | Passed | Passed since KB-316 |

### Claude Code

- 2026-11-08 — Windows 11 — 2.1.319 — `v0.2.0` (commit `9c29997`) — clean-profile install from `proprock/marketplace` (pinned `v0.2.0` since commit `01bbf01`); `plugin update` from `v0.1.1` to `v0.2.0` after the pin moved, then removal; files identical to each tag — passed (KB-318).
- 2026-11-08 — Linux (Debian bookworm container) — 2.1.319 — `v0.1.1` (commit `0f96da6`) and `v0.1.0` — clean-profile install of `v0.1.1`, files identical to the tag; rollback to the published `v0.1.0` by reinstalling from a catalog pinned to it, `plugin update` back to `v0.1.1`, removal; files identical to each tag — passed (KB-113).
- 2026-11-08 — Windows 11 — 2.1.316 — `v0.1.1` (commit `0f96da6`) — clean-profile install, seven commands, files identical to the tag; `plugin update` from the published `v0.1.0` to `v0.1.1` after the catalog pin moved; rollback to `v0.1.0` by reinstalling from a catalog pinned to it; files identical to each tag — passed (KB-023).
- 2026-11-07 — Windows 11 — 2.1.316 — `v0.1.0` (commit `c3867d0`) — clean-profile install, seven commands, files identical to the tag — passed (KB-023).
- 2026-10-30 — macOS — 2.1.308 — `v0.1.0-rc.2` and `v0.1.0-rc.3` (commit `e068b9d`) — clean-profile install of rc.2 (five commands) and rc.3 (seven commands, files identical to the tag); update between two pinned Git tags of a fixture repository (versions 0.1.0 and 0.1.1) with `plugin update`, and uninstall and reinstall also restored 0.1.0 — passed (KB-021).
- 2026-10-29 — Linux, macOS 26.6.2, Windows Server 2025 — 2.1.312 — local build — isolated local marketplace lifecycle; see the [validation record](validation.md) — passed (KB-011).
- 2026-10-29 — Linux — 2.1.312 — local build — authenticated skill discovery and explicit invocation, with profile caveats; see the validation record — passed (KB-008).
- 2026-10-29 — Linux — 2.1.301 — local working tree — strict metadata validation and isolated local marketplace lifecycle; see the validation record — passed (KB-005).
- 2026-10-29 — Linux — Claude Code and Codex — pilot tasks — behavior pilot trials recorded; the pilot alone did not meet the release gate, later runs did (see the [gate assessment](release-gate-assessment.md)) (KB-016).

### Codex CLI

- 2026-11-08 — Windows 11 — 0.160.0 and 0.167.0 — `v0.1.1` → `v0.2.0` → `v0.1.1` — remote install, update, rollback and removal between pinned Git tags (`scripts/smoke_codex_remote.py`), files identical to each commit — passed (KB-112).
- 2026-11-08 — Windows 11 — 0.160.0 — published `proprock/marketplace` (commit `fc34450`, pinned `v0.2.0`) — install from the published catalog — passed (KB-112).
- 2026-11-08 — Windows 11 — 0.160.0 and 0.167.0 — local build — isolated local marketplace lifecycle (`scripts/smoke_codex.py`) — passed (KB-112).
- 2026-10-29 — Linux (Ubuntu) — 0.165.0 — local build — isolated local marketplace lifecycle; see the [adapter guide](../adapters/codex/README.md) — passed (KB-103).
- 2026-10-29 — Linux (Ubuntu) — 0.165.0 — local build — authenticated skill discovery, with profile caveats; see the adapter guide — passed (KB-104).
- macOS — no Codex result yet (KB-114, KB-112).

### Packaging and release artifacts

- 2026-11-08 — Windows 11 — Python 3.14.3, zlib `1.3.1.zlib-ng` — commit `b47756a` — since KB-316 (stored entries, Unix system byte) a local build is byte-identical to the CI (Ubuntu) archives of the same commit (run 42503329826); before it, the `v0.1.0` build differed in bytes only — passed (KB-316).
- 2026-11-07 — Linux (CI) — `v0.1.0` — CI archives of `v0.1.0` are byte-identical to those of `v0.1.0-rc.3` — passed (KB-023).
- 2026-10-30 — Linux (CI, Ubuntu) and macOS (local build) — `v0.1.0-rc.2` — CI archives byte-identical to a local macOS build of the same tag; inventory, license and secret-pattern checks — passed (KB-019).
- 2026-10-29 — Linux, macOS, Windows (hosted CI) — Python 3.10 and 3.13 — package checks — passed (KB-007).

[Validation record](validation.md), [Codex adapter guide](../adapters/codex/README.md), and [comparison results](../tests/behavior/codex-comparison-results-2026-10-29.md) record scope and limitations. Portable files use LF and ordinary copies without Unix symlinks or shell scripts. OS portability still requires native runtime tests.

## Support statement for v0.2.0

Supported means tested at the points above, nothing broader. `v0.1.0` equals `v0.1.0-rc.3`, so the candidate evidence applies to it. `v0.1.1` changes only the init engine, the two init commands and the Codex init skills (KB-235, KB-227). `v0.2.0` removes the TDD red/green commit rule from the core (now the `tdd-commits` init feature, KB-228) and changes the init engine and its features (KB-210, KB-236, KB-237, KB-239, KB-240 to KB-242, KB-314, KB-317); skills and the other commands are those of `v0.1.0`. Installation from the published `v0.2.0` tag and `plugin update` from `v0.1.1` passed in clean profiles on Windows 11 with Claude Code 2.1.319 (KB-318); Linux and macOS were not repeated for `v0.2.0`.

- **Claude Code:** install, update, rollback and removal verified for the local marketplace on Linux, macOS and Windows (2.1.312), for the pinned remote candidate on macOS (2.1.308) for the pinned `v0.1.0` and `v0.1.1` on Windows (2.1.316: install, update from `v0.1.0`, rollback to it) and on Linux (2.1.319 in a Debian bookworm container: install, rollback, update, removal; KB-113). `/kaboost:init status` ran without approval prompts in `claude -p` on Windows with only `py -3` available (2.1.316, KB-227).
- **Codex CLI:** local marketplace lifecycle on Linux (0.165.0) and Windows 11 (0.160.0, 0.167.0); remote install from `proprock/marketplace`, update, rollback and removal between pinned tags on Windows 11 (0.160.0, 0.167.0; KB-112). macOS is untested. Skills only; the `/kaboost:*` commands do not exist for Codex.
- **Commands:** `/kaboost:plan`, `debug`, `verify`, `context`, `help` (Claude Code only). Only `plan` has a behavior measurement.
- **Not claimed:** any improvement in task outcome. Measured so far: skill routing and the written plan work as described; outcomes did not improve and cost per session rose (see the [calibration report](../tests/behavior/kb216-calibration-2026-10-30.md)). Hooks, MCP servers and background processes are not part of the toolkit.

Exact commands are in the [README](../README.md); migration is in [migration.md](migration.md).

## Client version and revalidation policy

`v0.2.0` has **no established supported version range or minimum**. The table records tested points only: Claude Code 2.1.301, 2.1.308 (remote candidate install, update and rollback on macOS), 2.1.312, 2.1.316 (remote install, update and rollback on Windows) and 2.1.319 (remote lifecycle on Linux for `v0.1.1`, install and update on Windows for `v0.2.0`), and Codex CLI 0.165.0 (local lifecycle on Linux), 0.160.0 and 0.167.0 (local and remote lifecycle on Windows; no macOS check). A passed lifecycle does not imply authenticated loading, instruction behavior, remote distribution, or release readiness. Other versions and client surfaces are unverified until evidence is recorded; patch releases are not automatically assumed compatible. A release must identify its exact tested toolkit commit, client versions, OS, and check scope before claiming support.

Review the client vendor's current primary documentation and release notes before adding a client, changing a tested client version, or preparing a release. Compare native manifest and catalog fields, installation/update/removal commands, skill discovery and instruction loading against the adapter and documented limitations. Record sources, date, version, affected surfaces, and any changed assumptions; a documentation review alone is not runtime evidence.

Repeat the relevant checks when the client version, OS, native package or catalog format, canonical skill metadata, installation procedure, or instruction activation changes; also repeat them after an observed regression or a vendor-announced breaking change. Run both package builders in check mode, both adapter validations, packaging tests, and the affected client's disposable-profile lifecycle harness. For changes to discovery or instruction semantics, additionally repeat authenticated discovery, explicit invocation and the affected core/precedence scenario; record profile caveats. Repeat remote install and rollback checks only when reviewed published refs are available, and rerun affected behavior scenarios when model-facing content or routing changes. A new OS or surface needs its own native evidence, not extrapolation.

The [Latest clients](../.github/workflows/latest-clients.yml) workflow runs every Monday (and on demand): it installs the newest Claude Code and the newest Codex CLI on Linux, macOS and Windows, and runs the disposable-profile lifecycle smoke tests (KB-313), for Codex also the remote lifecycle between the two newest tags and from the published catalog (KB-114). A failed scheduled run opens an issue titled "Latest clients failed" unless one is open. A pass there is an early signal, not a tested point for this table; a failure triggers the revalidation above.

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

# Validation record

Date: 2026-10-29. Environment: Linux; Python 3.10.12. Claude Code 2.1.301. Source: local working tree, unreleased 0.1.0 candidate.

| Command / check | Result | Limit |
| --- | --- | --- |
| `python3 scripts/build.py --check` | Passed | Canonical/generated equality; no runtime claim |
| `python3 scripts/validate.py` | Passed | Constrained canonical format, manifests, versions, local links, line budget, inventory |
| `python3 -m unittest discover -s tests/packaging -v` | Passed | Repeatability, tamper detection/repair, unknown-file preservation, unsafe paths, versions, symlink refusal |
| `python3 scripts/check_secrets.py` | Passed | Common credential patterns only |
| `claude plugin validate --strict .` | Passed | Native marketplace metadata |
| `claude plugin validate --strict plugins/ai-dev-toolkit` | Passed | Native plugin metadata |
| `python3 scripts/smoke_claude.py` | Passed | Local temporary profile only; no inference |

Lifecycle evidence: registered a local fixture, installed twice, found plugin in inventory, bumped fixture metadata to 0.1.1, refreshed catalog and updated plugin, observed 0.1.1, uninstalled, restored original metadata, reinstalled 0.1.0, uninstalled, and removed the catalog. Existing `env` settings sentinel survived every step. Temporary configuration was deleted afterward.

Pending: core loading and instruction interaction, negative/positive model routing, network-failure behavior, Git transport and published tag pinning, macOS/Windows native client lifecycle, and paired real-project behavior trials. No efficacy or full cross-platform support claim is made. Follow tests/behavior/README.md and docs/roadmap.md before release.

## Additional Linux checks — 2026-10-29

Source commit `565742507bc35982b623b460cb27d5139a5e1e85`; Linux x86_64, kernel 5.15.0-198-generic; Claude Code 2.1.312. `python3 scripts/build.py --check`, `python3 scripts/validate.py`, and all nine packaging unit tests passed. `python3 scripts/smoke_claude.py` passed the local lifecycle again with a disposable profile. It also passed with `TMPDIR='/tmp/kaboost path test'`, exercising marketplace and profile paths containing spaces. This is partial evidence for KB-012: Windows paths without symlink privileges remain untested. Neither lifecycle run invokes a model.

Hosted package checks passed on Linux, macOS, and Windows with Python 3.10 and 3.13 in [run 40877640914](https://github.com/proprock/kaBoost/actions/runs/40877640914), source commit `30102b7b7df82bf05e6603fb62d6caf2582656f7`. The earlier [failed run](https://github.com/proprock/kaBoost/actions/runs/40871832108) exposed a macOS temporary-directory symlink in tests and Windows line-ending conversion of LICENSE; the tested commit addresses both. This CI does not exercise native Claude installation or model behavior on those platforms.

Authenticated skill check (KB-008): on Linux with Claude Code 2.1.312 and local plugin 0.1.0, a newly created `CLAUDE_CONFIG_DIR` was installed and authenticated separately. Stream JSON initialization listed all three `ai-dev-toolkit` skills. A read-only prompt explicitly requested the `Skill` tool for `ai-dev-toolkit:project-context`; the event stream recorded that tool call, no permission denials, and a successful result. The account also synchronized other plugins into the new profile, so this is not an isolated account or evidence of skill routing without other plugins. Core imports and automatic routing were not tested by this check.

Core import check (KB-009, partial): an isolated user instruction and a project instruction with distinct markers were loaded together, and their hashes remained unchanged. When the project instruction imported a temporary local copy of the core rules via `@./core-rules.md`, a model call with tools disabled reported both markers and a specific rule from that copy. With the documented absolute path to the checkout, the model instead reported that it had received the import path but not its contents; a subsequent read was denied by Claude permissions. An additional call with an explicitly granted `Read(//home/antonpadapryhara/Documents/repos/kaBoost/core/engineering-rules.md)` permission successfully read that single file and reported its rule alongside both markers; this was a tool read, not evidence of automatic import. The documented absolute-path automatic import remains unverified; this check does not establish general instruction precedence.

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

Pending: authenticated skill/core loading, negative/positive model routing, network-failure behavior, Git transport and published tag pinning, macOS/Windows native client lifecycle, hosted CI execution, and paired real-project behavior trials. No efficacy or full cross-platform support claim is made. Follow tests/behavior/README.md and docs/roadmap.md before release.

## Additional Linux checks — 2026-10-29

Source commit `565742507bc35982b623b460cb27d5139a5e1e85`; Linux x86_64, kernel 5.15.0-198-generic; Claude Code 2.1.312. `python3 scripts/build.py --check`, `python3 scripts/validate.py`, and all nine packaging unit tests passed. `python3 scripts/smoke_claude.py` passed the local lifecycle again with a disposable profile. It also passed with `TMPDIR='/tmp/kaboost path test'`, exercising marketplace and profile paths containing spaces. This is partial evidence for KB-012: Windows paths without symlink privileges remain untested. Neither lifecycle run invokes a model.

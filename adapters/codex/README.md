# Codex adapter

Run `python scripts/build_codex.py` from the repository root to generate the
package in `adapters/codex/package/ai-dev-toolkit`; use `--check` to detect
drift. The package contains both the Agent Plugins manifest and a Codex
compatibility manifest. Skills and the referenced workflow are copied from
the canonical sources, and the checksum inventory covers the package files.
The build does not change client configuration or delete unexpected files.

## Local CLI lifecycle

From the repository root, after reviewing the source and building the package:

```sh
python scripts/build_codex.py --check
codex plugin marketplace add ./adapters/codex
codex plugin add ai-dev-toolkit@kaboost-codex
codex plugin list
```

These commands modify the active Codex profile. Start a new session after
installation. For an update, switch this checkout to the desired reviewed
version, rebuild it if needed, and re-run `codex plugin add` with the same
selector. Roll back by restoring a previously reviewed version and re-running
the same add command. Version changes were tested; refreshing changed files
under the same version was not. A Git tag alone is not proof of immutability.
To remove the plugin and then its catalog:

```sh
codex plugin remove ai-dev-toolkit@kaboost-codex
codex plugin marketplace remove kaboost-codex
```

## Core activation and precedence

The included core rules are reference material; installing the plugin does not
activate them. For a project choosing to use them, copy
`core/engineering-rules.md` into a project-owned file and explicitly instruct
Codex to read it in the project's existing `AGENTS.md`. Review and merge with
existing instructions rather than replacing them; don't assume Markdown links
are automatic imports. Updates to the plugin do not update the project copy.

On Ubuntu, one authenticated Codex CLI 0.165.0 session using model
`gpt-6.1-sol` read the project-local rules when instructed by the project
`AGENTS.md`. In the same session, a project marker won over a conflicting global
marker. This is one behavioral observation, not a guarantee of instruction
following or evidence for every precedence conflict, client, or environment.

`python scripts/smoke_codex.py` exercises a disposable local marketplace on
the installed CLI, without model calls. On Ubuntu with Codex CLI 0.165.0 it
passed local install, repeated install, re-add after a version change, rollback
and removal; the test version is a fixture, not a published release. This does
not verify plugin skill discovery in a clean authenticated profile, remote
distribution, other operating systems, or the desktop and IDE clients.

For the disposable catalog format and instruction ordering, see the official
[plugin documentation](https://developers.openai.com/plugins/build/plugins) and
[Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide).
This package remains unreleased.

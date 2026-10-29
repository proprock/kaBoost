# kaBoost — AI Development Toolkit

A small, versioned engineering toolkit: understand before changing code, choose a simple complete solution, and verify the result. Three on-demand skills support project context, systematic debugging, and verification. Core rules are language-agnostic; project tooling stays local.

**Status:** 0.1.0 candidate, not published. Claude Code and Codex CLI have local adapters. See [compatibility](docs/compatibility.md) for tested versions, evidence and untested combinations. No installer, background sync, hooks, runtime scripts, or bundled MCP servers. Installing a plugin does **not** activate global engineering rules.

## Quick start

Requires Git and an installed Claude Code client. The local procedure works from Bash, zsh, or PowerShell, with no symlinks or Python dependency:

```text
git clone https://github.com/proprock/kaBoost.git
cd kaBoost
claude plugin marketplace add ./
claude plugin install ai-dev-toolkit@ai-dev-toolkit
```

Restart Claude Code. Invoke a skill explicitly, for example:

```text
/ai-dev-toolkit:project-context Inspect this repository and report context without writing files.
/ai-dev-toolkit:systematic-debugging Investigate the failing regression test.
/ai-dev-toolkit:verification Check this change against the ticket acceptance criteria.
```

After a release is published, pin the marketplace to a reviewed tag and verify that it points to the expected commit. Replace VERSION with an existing release tag (no v0.1.0 tag is published by this change):

```text
claude plugin marketplace add https://github.com/proprock/kaBoost.git#VERSION
claude plugin install ai-dev-toolkit@ai-dev-toolkit
```

Unpinned convenience installation in a Claude session:

```text
/plugin install ai-dev-toolkit --marketplace proprock/kaBoost
```

This remote command works only after the package has been pushed. Local installation is available immediately.

## Activate core rules separately

Review [core/engineering-rules.md](core/engineering-rules.md). For a project, copy the reviewed file into the project, for example as `.claude/engineering-rules.md`, and add an import to the existing project CLAUDE.md; retain its other contents:

```text
@.claude/engineering-rules.md
```

The copy is user-managed: review and update it alongside the plugin. In a Claude Code 2.1.312 print-mode test on Linux, an import outside the project did not automatically load the file contents; do not assume that an absolute checkout path activates the rules. Verify loading in your own client and profile. Never replace an existing CLAUDE.md with a generated file. [Project example](examples/project/CLAUDE.md).

## Updates and removal

For a moving local/development source, rebuild or update its checkout, then:

```text
claude plugin marketplace update ai-dev-toolkit
claude plugin update ai-dev-toolkit@ai-dev-toolkit
```

A pinned tag intentionally stays pinned. To change releases, uninstall the plugin, remove the marketplace, add the new tag, and reinstall. Rollback uses the same steps with the previous tag. Restart the session and verify `claude plugin list`. Do not edit the plugin cache; keep overrides in user/project rules. Review and update the separate project-local core copy explicitly too.

```text
claude plugin uninstall ai-dev-toolkit@ai-dev-toolkit
claude plugin marketplace remove ai-dev-toolkit
```

Remove only the core import you added. No toolkit command edits your global instruction files. See the [Claude adapter](adapters/claude-code/README.md) for lifecycle limits.

## Maintain and verify

Python 3.10+ is needed only for maintainers. On Windows replace `python3` with `py -3`:

```text
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/validate.py
python3 -m unittest discover -s tests/packaging -v
claude plugin validate --strict .
claude plugin validate --strict plugins/ai-dev-toolkit
python3 scripts/smoke_claude.py
```

The optional smoke test uses a disposable Claude profile and local package; it makes no model calls. Build refuses unknown package files instead of deleting them. SHA256SUMS.json detects corruption against a trusted release; it does not authenticate its own source. Review unfamiliar instructions and metadata before installing them.

[Architecture](docs/architecture.md) · [Decisions](docs/decisions/README.md) · [Roadmap](docs/roadmap.md) · [TODO](TODO.md) · [DONE](DONE.md) · [Environment boundary](docs/sync-boundary.md) · [Evaluation](tests/behavior/README.md)

Track unfinished work in TODO.md. Move completed tasks or fully completed sections to DONE.md with a completion date and verification evidence; do not duplicate them across files.

Apache-2.0. Toolkit wording is an original synthesis; verify upstream licenses before copying external content.

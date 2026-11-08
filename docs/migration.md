# Local overrides and migration

The current release is `v0.2.0`. Use this procedure for reviewed versions. Keep
user and project instructions and any customized core copy under their owner's
control, outside plugin caches and generated package directories. A cache edit
can be replaced by an update and is not a durable override.

1. Record the current toolkit commit, client version, installed plugin identity,
   and where the project-local core copy and instruction files live. Preserve a
   recoverable copy of user-owned changes according to the project's policy.
2. Review the target commit, changelog, compatibility evidence and generated
   package. Compare the old and new canonical core and skills with local
   instructions and customizations. Identify duplicate skills and conflicting
   instructions; do not assume one universal precedence across clients.
3. Resolve conflicts explicitly with the owner: retain the intended project
   behavior in the appropriate user or project instruction, and remove or
   adjust a duplicate only after checking ownership. Codex has been observed
   to list a standalone skill and plugin skill separately; namespacing does not
   eliminate the duplicate. Do not overwrite local files automatically.
4. Apply the client-specific upgrade procedure in the [Claude guide](../adapters/claude-code/README.md)
   or [Codex guide](../adapters/codex/README.md). Check plugin identity and
   version, restart the session, and verify the needed skill and instruction
   behavior in the actual project. Updating a plugin does not update a separate
   project-owned core copy: review and merge that copy deliberately.
5. If verification fails, restore the previously reviewed package version using
   the same client procedure, restore any separately changed project-owned files
   from the owner's backup, restart, and recheck. Keep evidence of failures and
   unresolved conflicts; a successful inventory check alone does not prove
   skill loading or correct model behavior.

The disposable lifecycle harnesses seed a profile setting plus user and project
instruction files and a project-owned core-copy sentinel. They check the setting
and byte-for-byte contents after each install, update, rollback and removal.
This checks those fixtures only; client-managed plugin registration can change,
and arbitrary user configuration, real release migration, remote tags, runtime
instruction precedence and other operating systems need separate evidence.

On 2026-10-29, both enhanced harnesses passed on Ubuntu with Claude Code
2.1.312 and Codex CLI 0.165.0, using local fixture metadata versions 0.1.0 and
0.1.1 and disposable profiles. These are fixture updates, not published releases;
no model was invoked during these checks.

## Moving from v0.1.1 to v0.2.0

The package version changes, so a normal update works after the catalog pin moves:

```text
claude plugin marketplace update proprock
claude plugin update kaboost@proprock
```

Restart the session, then run `/kaboost:init status` in each project (and `/kaboost:init-global status`). Unlike the 0.1.1 update, some blocks it wrote change:

- **Core rules:** the TDD red/green commit rule left the core (KB-228). Copies written by `core-rules` and `core-rules-global` show as outdated and keep the old rule until you apply them again. A project that wants the rule enables the `tdd-commits` feature, which also ships `scripts/kaboost_audit_tdd.py`.
- **CI templates:** an unedited `ci-python` workflow shows as outdated (actions v7, `setup-uv` v10, the `.github/apt-packages.txt` step). The v7 actions need GitHub Actions runner 2.327.1 or later; update self-hosted runners before applying it.
- **TODO and DONE:** an unedited `todo-done` pair shows as outdated (one line per task, grep commands, hex ids). A `TODO.md` that already holds your tasks shows as drift with advice; nothing is overwritten, and you copy the new rules by hand if you want them.

A block you edited by hand stays as it is until you review it; `--force` overwrites it.

## Moving from v0.1.0 to v0.1.1

The package version changes, so a normal update works after the catalog pin moves:

```text
claude plugin marketplace update proprock
claude plugin update kaboost@proprock
```

Restart the session. Blocks already written by `/kaboost:init` stay valid. In a repository whose `CLAUDE.md` imports `AGENTS.md` while `AGENTS.md` carries the core for Codex, `/kaboost:init status` now reports the duplicate core and the command that removes the Claude copy.

## Moving from a release candidate to v0.1.0

The candidates `v0.1.0-rc.N` and the release `v0.1.0` all carry the package
version 0.1.0, so do not rely on `claude plugin update` to notice the move.
After the catalog pin moves, refresh the catalog and reinstall:

```text
claude plugin marketplace update proprock
claude plugin uninstall kaboost@proprock
claude plugin install kaboost@proprock
```

Restart the session and check `claude plugin list`. Project-local core copies
and blocks written by `/kaboost:init` are not touched; run `/kaboost:init status`
in a project to see whether a block is outdated.

## Migrating from the pre-candidate names

Before `v0.1.0-rc.2` the plugin and the local marketplace were both called
`ai-dev-toolkit`. They are now:

| Before | Now |
| --- | --- |
| `ai-dev-toolkit@ai-dev-toolkit` (local checkout) | `kaboost@kaboost-local` |
| `/plugin install ai-dev-toolkit --marketplace proprock/kaBoost` | `kaboost@proprock` from `https://github.com/proprock/marketplace.git` |
| skills `/ai-dev-toolkit:<skill>` | `/kaboost:<skill>` |
| `plugins/ai-dev-toolkit`, `adapters/codex/package/ai-dev-toolkit` | `plugins/kaboost`, `adapters/codex/package/kaboost` |

The two names are different plugins to the client, so an update does not carry
over. Remove the old install and add the new one:

```text
claude plugin uninstall ai-dev-toolkit@ai-dev-toolkit
claude plugin marketplace remove ai-dev-toolkit
claude plugin marketplace add https://github.com/proprock/marketplace.git
claude plugin install kaboost@proprock
```

Project-local core copies and instruction files are not touched by these
commands. Update any project text that names `/ai-dev-toolkit:` skills.
Historical behavior reports keep the old name.

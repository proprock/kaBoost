# Local overrides and migration

The toolkit is unreleased. Use this procedure for reviewed local versions; a
future published release needs its own reviewed ref and release notes. Keep
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

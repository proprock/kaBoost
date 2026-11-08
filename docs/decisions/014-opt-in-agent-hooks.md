# 014: Opt-in agent hooks through init

Status: accepted (2026-11-08, KB-226)

## Context

[ADR 007](007-explicit-commands.md) kept Claude Code and Codex agent hooks out of scope "until commands are shown insufficient", and [ADR 009](009-init-engine.md) repeated that for `init`. Since then the evidence points to rules that the model reads but does not always follow: a checklist in the core gave 0/10 ([ADR 006](006-planning-entry-point.md)), and a visible plan names a risk without forcing action ([ADR 008](008-evaluation-criteria.md)). Some rules are mechanical and can be checked before the action instead. The first case is the rule that the `precommit-hooks` feature adds: never commit with `--no-verify`. A pre-commit hook cannot enforce it, because `--no-verify` skips that hook.

Both clients now document the same hook shape. Claude Code reads `hooks` from `.claude/settings.json` (project) or `~/.claude/settings.json` (user): an event such as `PreToolUse`, a `matcher` on the tool name (`Bash`), and `command` handlers that receive the tool call as JSON on stdin and block it by exiting with code 2 (stderr shown to the model) or by printing a `permissionDecision` of `deny`. Codex reads the same structure from `hooks.json` or from `[[hooks.PreToolUse]]` in `config.toml`, behind `[features] hooks = true`, and passes `tool_name` and `tool_input` the same way. Sources: [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Codex hook schema](https://github.com/openai/codex/tree/main/codex-rs/hooks/schema). Verify both again against the installed clients before implementing.

## Decision

1. Agent hooks may be shipped only as opt-in `init` features. They are offered, previewed, written after confirmation and removed by disabling, like other features. The plugin and Codex package manifests declare no hooks, so installing kaBoost still runs nothing.
2. Project scope only. A hook goes into the repository's settings, where the team sees and reviews it; no global hook is written.
3. A check that concerns the commit itself goes into a git hook (the existing `git-hook` kind), which works for every client and for people. An agent hook is used only for what git cannot see, such as the agent passing `--no-verify`.
4. The hook script is a file kaBoost owns (`own` mode, for example `.claude/hooks/kaboost_no_verify.py`), so the existing hash-based drift detection covers it. The settings entry that calls the script is identified by that script path, not by markers, because JSON and TOML have no comments.
5. First version: the engine creates the settings file when it does not exist, with the kaBoost entry only, and deletes it on disable, which keeps the byte-exact restore of KB-221. When the file exists, the feature is a conflict, and its hint shows the entry to add by hand. Merging into an existing JSON or TOML file (add and remove only the entry that names the kaBoost script, keep everything else byte for byte) comes later, when a user hits that conflict.
6. First hook: `no-verify-guard`. It is a `PreToolUse` hook on `Bash` that blocks `git commit` with `--no-verify` or `-n`, and `git push --no-verify`, and tells the agent to fix the failing check instead. It is offered together with `precommit-hooks`. The TDD red/green check from [ADR 011](011-tdd-red-green-commits.md) becomes a `commit-msg` git hook under point 3, not an agent hook.

## Alternatives and tradeoffs

- **Keep hooks out of scope.** Nothing runs on the user's machine, but the `--no-verify` rule stays advice only, and the project ignores its own evidence that written rules are not enough.
- **Hooks in the plugin manifest.** Simplest to ship, but always on for everyone who installs kaBoost and outside the project's review. That breaks opt-in.
- **Global hooks.** Cover every repository at once, but change projects the user did not choose, against the "no global mandate" requirement of the language packs.
- **JSON/TOML merge from the start.** Covers repositories that already have settings, but needs a new managed-entry mechanism before there is any demand. Point 5 postpones it.

## Consequences

- Supersedes the hooks part of the scope boundary in ADR 007 and the sentence in ADR 009 that keeps agent hooks out of `init`. Agents, MCP integrations and Jira connectors stay out of scope.
- A hook runs code on the user's machine on every matching tool call. The preview shows the script and the settings entry in full, and the script uses only the Python standard library.
- Codex hooks are a stable feature that is on by default in Codex CLI 0.160.0 (`codex features list`), so `init` changes no Codex configuration. Codex runs a project hook only after the user trusts the project and the hook; until then the hook does nothing, and the feature summary says so.
- Implementation (KB-226): the `no-verify-guard` feature, `mode: exact` in the engine for JSON files. Verified on Windows 11: Claude Code 2.1.319 runs project hooks through Git Bash and blocked `git commit --no-verify`. Codex CLI 0.160.0 ran the project hook only after the maintainer trusted it, passed the plain command in `tool_input.command` (it runs it through PowerShell afterwards; the guard also unwraps `powershell -Command` and `bash -c`), and reported exit code 2 as a failed hook while running the command anyway. The guard therefore exits 0 with a `PreToolUse` `permissionDecision: "deny"`, which both clients document and which blocked the commit in Codex, both in `codex exec` and in an interactive session (KB-247).
- Whether the guard changes behavior is measured as a miss-log count ([ADR 013](013-cost-per-pass-and-miss-log.md)): `--no-verify` commits before and after enabling it.

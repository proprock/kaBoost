---
description: Add personal practices to your global Claude Code and Codex instruction files (previewed, confirmed, reversible)
argument-hint: [status|disable]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py *)
disable-model-invocation: true
---
Add personal practices from the kaBoost catalog to the user's global instruction files: `~/.claude/CLAUDE.md` for Claude Code and `~/.codex/AGENTS.md` for Codex. These files are outside any project and apply to every project, so be explicit about that. Only the bundled script edits files; never edit them yourself. Argument: $ARGUMENTS

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py" status --scope global` and read the JSON. If the argument is `status`, show the table below and stop. A tool whose directory (`~/.claude`, `~/.codex`) does not exist is not offered unless the user asks for it.
2. Show the features with their state (enabled, disabled, outdated, partial, drift, conflict) and which tool files each touches. Say that the core rules entry makes the engineering rules apply in every project.
3. Ask with AskUserQuestion (multiSelect, at most four options per question, continue in further rounds) which features to enable and which enabled ones to disable (only disable if the argument is `disable`), and for which tools (Claude Code, Codex, or both). Stop if nothing is chosen.
4. Preview without `--yes`: `python3 "${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py" apply --scope global --ids <ids> [--targets claude,codex]` (or `disable`). Show every diff in full, because these are the user's personal files, and list skipped features with their reasons.
5. Ask for confirmation naming each file. Only after a clear yes, run the same command with `--yes`. Do not use `--force` unless the user has reviewed a hand-edited block and asks for it.
6. Report what was written, where the backups (`*.kaboost-bak-*`) are, and what was skipped and why. Disabling removes only the managed block and restores the file; text outside the block is never changed.

Nothing here runs at installation or in the background.

---
description: Add practices from the kaBoost catalog to this repository (previewed, confirmed, reversible)
argument-hint: [status|disable]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py *)
disable-model-invocation: true
---
Add practices from the kaBoost catalog to the current repository. This command sets up Claude Code only (`CLAUDE.md`, `.claude/`) plus the files both tools share (`AGENTS.md`, `TODO.md`, `Makefile`, ...); Codex has its own skill that writes its entries to `AGENTS.md`. Always pass `--targets claude`. Only the bundled script edits files; never edit these files yourself. Argument: $ARGUMENTS

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py" status --scope repo --targets claude` and read the JSON. If the argument is `status`, show the table below and stop.
2. Show the features grouped by `group` with their state: enabled, disabled, outdated, partial, drift, or conflict. For drift and conflict give the reason from `edits[].note`. Features that do not fit this repository are not listed.
3. Ask what to change with AskUserQuestion (multiSelect), one question per group, at most four options per question and four questions per round; continue in further rounds if there are more. Ask which disabled or outdated features to enable and which enabled features to disable; if the argument is `disable`, ask only about disabling. Stop if nothing is chosen.
4. Preview without `--yes`: `python3 "${CLAUDE_PLUGIN_ROOT}/init/kaboost_init.py" apply --scope repo --targets claude --ids <ids>` (or `disable`). Summarize each file (create, modify, delete), show short diffs, list the `commands` the script will run (for example installing a git hook) and skipped features with their reasons.
5. Ask for confirmation. Only after a clear yes, run the same command again with `--yes`. Do not use `--force` unless the user has reviewed a hand-edited block and asks for it.
6. Report what was written, where the backups (`*.kaboost-bak-*`) are, and what was skipped and why. Disabling removes only the managed block and restores the file.

Features applied once are shown as enabled on the next run; running the command again never duplicates them.

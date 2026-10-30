---
name: kaboost-init
description: Add kaBoost catalog practices to the current repository for Codex. Invoke explicitly with $kaboost-init; never use implicitly.
---
Add practices from the kaBoost catalog to the current repository for Codex. Use this skill only when the user invokes `$kaboost-init`. Only the bundled script edits files; never edit these files yourself. This skill writes Codex's entries and the files both tools share (`AGENTS.md`, `TODO.md`, `Makefile`, ...); the Claude Code command handles `CLAUDE.md` and `.claude/`. Always pass `--targets codex`.

The script is `init/kaboost_init.py` in this plugin, two directories above this file (`../../init/kaboost_init.py`). Resolve it to an absolute path from this file's location and call it as `python3 <script>`; run it from the repository root, or pass `--root`.

1. Run `python3 <script> status --scope repo --targets codex` and read the JSON. If the user only asked for status, show the table below and stop.
2. Show the features grouped by `group` with their state: enabled, disabled, outdated, partial, drift, or conflict. For drift and conflict give the reason from `edits[].note`. Features that do not fit this repository are not listed.
3. Ask in plain text, one group at a time with a numbered list, which disabled or outdated features to enable and which enabled ones to disable (only disabling if the user asked to disable). Stop if nothing is chosen.
4. Preview without `--yes`: `python3 <script> apply --scope repo --targets codex --ids <ids>` (or `disable`). Summarize each file (create, modify, delete), show short diffs, and list skipped features with their reasons.
5. Ask for confirmation. Only after a clear yes, run the same command again with `--yes`. Do not use `--force` unless the user has reviewed a hand-edited block and asks for it.
6. Report what was written, where the backups (`*.kaboost-bak-*`) are, and what was skipped and why. Disabling removes only the managed block and restores the file.

Features applied once are shown as enabled on the next run; running the skill again never duplicates them. Nothing here runs at installation or in the background.

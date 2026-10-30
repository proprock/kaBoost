---
name: kaboost-init-global
description: Add kaBoost personal practices to the global Codex instruction file. Invoke explicitly with $kaboost-init-global; never use implicitly.
---
Add personal practices from the kaBoost catalog to the user's global Codex instruction file `~/.codex/AGENTS.md`. This file is outside any project and applies to every project, so be explicit about that. Use this skill only when the user invokes `$kaboost-init-global`. This skill edits only Codex's file; the Claude Code command handles `~/.claude/CLAUDE.md`. Only the bundled script edits files; never edit them yourself. Always pass `--targets codex`.

The script is `init/kaboost_init.py` in this plugin, two directories above this file (`../../init/kaboost_init.py`). Resolve it to an absolute path from this file's location and call it as `python3 <script>`.

1. Run `python3 <script> status --scope global --targets codex` and read the JSON. If the user only asked for status, show the table and stop.
2. Show the features with their state (enabled, disabled, outdated, partial, drift, conflict) and the file each touches. Say that the core rules entry makes the engineering rules apply in every project.
3. Ask in plain text, with a numbered list and at most four options per round, which features to enable and which enabled ones to disable (only disabling if the user asked to disable). Stop if nothing is chosen.
4. Preview without `--yes`: `python3 <script> apply --scope global --targets codex --ids <ids>` (or `disable`). Show every diff in full, because this is the user's personal file, and list skipped features with their reasons.
5. Ask for confirmation naming the file. Only after a clear yes, run the same command with `--yes`. Do not use `--force` unless the user has reviewed a hand-edited block and asks for it.
6. Report what was written, where the backups (`*.kaboost-bak-*`) are, and what was skipped and why. Disabling removes only the managed block and restores the file; text outside the block is never changed.

Nothing here runs at installation or in the background.

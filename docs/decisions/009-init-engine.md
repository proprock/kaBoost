# 009: Init engine

Status: accepted

## Decision

`/kaboost:init` (repository) and, later, `/kaboost:init-global` (personal files) change files only through a bundled script, `init/kaboost_init.py`, which uses the Python standard library and runs only when the user invokes the command. The command text guides the conversation (feature choice, preview, confirmation); the script reads a catalog (`init/catalog.json` and `init/features/`) and writes marked blocks. The model never edits these files directly.

Each change is a block between `kaboost:begin` and `kaboost:end` markers carrying a version, a content hash, and what is needed to restore the original bytes. Editing inside a block is detected as drift and never overwritten without an explicit `--force`; damaged markers and unmanaged files that a feature would own are refused; changes are previewed by default and written only with `--yes`, with a backup next to each modified file.

## Evidence and reasons

- The acceptance criterion, apply then re-apply with no change then disable restoring the exact bytes, can be tested deterministically on disposable directories; a model editing files cannot be tested that way except by costly, nondeterministic sessions.
- The script keeps all state in the files themselves, so no extra state file is added to a repository.

## Consequences

- Amends the earlier statement that the toolkit has no runtime scripts: the init engine is the single exception. It is not run at installation or in the background, and `hooks` stay out of scope (ADR 007).
- Requires `python3` on the machine when `init` is used. The commands do nothing else without it.
- Codex has no plugin commands; its operations are a separate task (KB-224) that reuses this engine.
- Global edits happen only through `/kaboost:init-global` after explicit confirmation; plugin installation never edits global files.
- Each tool edits only its own files. Catalog edits carry an optional `tool`; `--targets` is a validated list (`claude,codex`, or `all`). Claude commands always pass `--targets claude`, the Codex skills (KB-224) will pass `--targets codex`. Edits without a `tool` are shared files (`AGENTS.md`, `TODO.md`, `Makefile`, ...) and apply for every target. Core rules reach Codex as a block in `AGENTS.md`, since Codex has no import syntax.

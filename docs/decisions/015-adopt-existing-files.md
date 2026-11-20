# 015: Adopt an existing TODO.md, DONE.md or CHANGELOG.md

Status: accepted (2026-11-20, KB-252), option A. Implementation: KB-255.

## Context

The `todo-done` and `changelog` features of `/kaboost:init` own their files (`mode: own`): the whole file is one kaBoost block, created from a template. When the file exists without markers, `plan_apply` refuses and `status` reports `conflict`, with a hint to copy the rules by hand. On 2026-11-15 `status` showed `conflict` for `todo-done` in kaBoost, aHerald and watchdog, and for `changelog` in kaBoost and aHerald; on 2026-11-20 kaBoost still shows both. Every mature repository already has these files, so the two most common practices cannot be enabled where they matter.

`own` has a second problem even in new repositories: the user's tasks and entries are written inside the block, so the block drifts with the first task and stays `drift` from then on. The hints say so ("TODO.md holds your tasks, so kaBoost does not rewrite it"), which means an updated tracking rule never reaches a repository that uses the feature.

Engine facts the options rely on ([ADR 009](009-init-engine.md), `init/kaboost_init.py`): an `append` edit adds a block at the end of an existing file and records the newlines it added before the block (`pre`), so `disable` restores the original bytes; drift is the block's content hash, so text outside the block is never drift; `one_line_entries` is checked by `line_warnings` on the whole file once the block exists.

## Options

### A. A second edit in `append` mode that holds only the rules

Split each template into rules and skeleton. The rules (the tracking rules of `TODO.md`, the one-line format of `DONE.md`, the "write for the user, add the entry in the same change" paragraph of `CHANGELOG.md`) become a block in `append` mode under a heading such as `## kaBoost tracking rules`. When the file does not exist, the engine creates it with the skeleton (headings and the example line) outside the block and the rules block; when it exists, it adds only the rules block.

- Placement: `append` puts the block at the end of the file. Putting it at the top, where an agent reads it first, needs a new insertion point (after the first `#` heading) and a second recorded newline count for the restore. The first version could keep the end and add the top position only if agents miss rules there.
- `disable`: removes the block and the newlines recorded in `pre`; the user's bytes come back exactly. A file the engine created (`created=1`) whose remaining text is only the untouched skeleton could be deleted, as today.
- Drift: only the rules are hashed, so tasks and changelog entries never cause drift, and a new rule version reaches the repository as `outdated`. This also fixes the permanent `drift` of `own` described above.
- `one_line_entries`: `line_warnings` already checks the whole file. In a repository whose tasks span several lines (kaBoost's own `TODO.md` uses indented sub-bullets), enabling the feature produces a warning until the user changes the format or the rule is relaxed. The preview should say this before the user confirms.
- Cost: no new mode; a catalog change, a template split, a migration for repositories that already have an `own` block (the block becomes the rules block plus text outside it), and a version bump.

### B. A new mode that wraps an existing rules section

When the existing file has a section whose heading matches (for example `## Tracking rules`), put markers around that section and replace its content with kaBoost's rules.

- `disable` must restore the user's original section, which the markers do not hold (they carry only a hash). That needs the original text stored somewhere: in the block (the file grows by a copy of the old section) or in a state file (which ADR 009 rules out: all state lives in the files).
- Drift and `one_line_entries` work as in A.
- It applies only to files that already have a matching heading; other files still conflict, so A would be needed anyway.

### C. Keep the manual hint

No engine change. The conflict and the hint stay, the practices cannot be enabled in a repository that has the files, and the rules are not updated where they were copied by hand.

## Recommendation

Option A with the block at the end of the file in the first version, the preview stating the `one_line_entries` consequence, and a migration of existing `own` blocks. It reuses the `append` mechanics that already restore bytes exactly, removes the conflict and the permanent drift, and needs no new state. B is rejected because restoring the replaced section needs state that ADR 009 excludes, and it covers fewer files than A. C leaves the problem as it is.

## Tests the implementation needs

- Apply on an existing `TODO.md`, `DONE.md` and `CHANGELOG.md` (LF, CRLF, BOM, no trailing newline, empty file) keeps every byte outside the block.
- Re-apply changes nothing; `status` shows `enabled`.
- `disable` restores the original bytes for each case above.
- A task added outside the block leaves the state `enabled`; a changed rule in the catalog shows `outdated` and applies without `--force`.
- A new repository gets the skeleton and the block; `disable` there deletes a file that holds only the untouched skeleton and keeps one that has user entries.
- A repository with an existing `own` block is migrated: apply turns it into the rules block plus the same entries outside it, and nothing the user wrote is lost.
- With multi-line tasks the preview of `apply` and `status` both carry the `one_line_entries` warning.

## Consequences if accepted

- An implementation task is added to TODO.md; KB-252 closes with this record.
- The `conflict` hints of both features go away; `summary` in the catalog stops saying "refuses if the file already exists".
- The `todo-done` rules then apply to repositories with their own established format; whether the one-line rule should be relaxed for indented sub-bullets is a separate decision.

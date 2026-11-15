# Backlog

Unfinished work only. Completed tasks move to DONE.md with the date and links to the evidence.

## Tracking rules

- Give every new task a permanent identifier in the form `<prefix>-<hex-ID>`, using four random hex digits, and keep it when moving or reordering the task. If tasks already exist, choose the prefix by analogy with their identifiers; otherwise, choose an abbreviation of the project name. For example, a new Watchdog project can use `WD-a3f9`, and a new kaBoost project can use `KB-7c2e`; if existing tasks use `APP-1234`, use `APP-b4e1` for a new task. Check with grep that the new id is unused in both files.
- Keep each task on one line that starts with `- [ ] <id>:`. The line has no length limit: it holds the title, the context, the intended approach and the acceptance criteria. List the backlog with `grep -n '^- \[ \]' TODO.md` and read one task with `grep '<id>:' TODO.md DONE.md`; read by id, not by line windows, because line numbers move with every edit.
- Keep only unfinished tasks here, as unchecked boxes. Check a task off only when its acceptance criteria have evidence.
- Move completed tasks to DONE.md with the completion date (YYYY-MM-DD) and links to the evidence.
- A deferred task stays unchecked with a reason and a condition for revisiting it.

## Tasks

- [ ] WD-a3f9: Describe the first Watchdog task and its acceptance criteria.

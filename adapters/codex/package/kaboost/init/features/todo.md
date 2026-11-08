# Backlog

Unfinished work only. Completed tasks move to DONE.md with the date and links to the evidence.

## Tracking rules

- Give every task a permanent identifier and keep it when moving or reordering tasks. A prefix and number (`TASK-001`) suits one line of work; when several branches add tasks at once, use four random hex digits (`#a3f9`) so they cannot pick the same next number. Check with grep that a new id is unused in both files.
- Keep each task on one line that starts with `- [ ] <id>:`. List the backlog with `grep -n '^- \[ \]' TODO.md` and read one task with `grep '<id>:' TODO.md DONE.md`; read by id, not by line windows, because line numbers move with every edit.
- Keep only unfinished tasks here, as unchecked boxes. Check a task off only when its acceptance criteria have evidence.
- Move completed tasks to DONE.md with the completion date (YYYY-MM-DD) and links to the evidence.
- A deferred task stays unchecked with a reason and a condition for revisiting it.

## Tasks

- [ ] TASK-001: Describe the first task and its acceptance criteria.

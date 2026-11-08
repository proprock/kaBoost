"""git commit-msg check for TDD red/green commits (kaBoost tdd-commit-hook).

Called by .git/hooks/commit-msg with the message file. A message without a `TDD: red` or `TDD: green` trailer is not
checked. A red commit must name a task ID ('KB-7: ...' or '... (KB-7)') and have an `Expected failing:` line; a
green commit must name a task ID that has a red commit in recent history. Only the message is checked: whether the red
commit holds only tests, and whether the tests fail and pass, is left to scripts/kaboost_audit_tdd.py. On
`--amend` the history still holds the commit being replaced, so a reworded green is checked leniently. Any error of
its own (git missing, unreadable file) lets the commit through. Standard library only.
"""
import os
from pathlib import Path
import re
import subprocess
import sys

TASK = re.compile(r'^([A-Za-z]+-\d+)\b|\(([A-Za-z]+-\d+)\)\s*$')
TRAILER = re.compile(r'^TDD:\s*(red|green)\s*$', re.M | re.I)
SCISSORS = re.compile(r'^\S -{8,} >8 -{8,}$', re.M)
HISTORY = 500


def task_of(message):
    lines = message.strip().splitlines()
    match = TASK.search(lines[0]) if lines else None
    return (match.group(1) or match.group(2)) if match else None


def git_executable():
    """git from PATH, skipping the current directory and anything under it. Windows looks in the current directory
    (here the repository) before PATH, so a bare 'git' could run a git.exe that a checked-out branch added."""
    here = Path.cwd().resolve()
    names = ('git.exe',) if os.name == 'nt' else ('git',)
    for entry in os.environ.get('PATH', '').split(os.pathsep):
        if not entry.strip():
            continue
        folder = Path(entry).resolve()
        if folder == here or folder.is_relative_to(here):
            continue
        for name in names:
            candidate = folder / name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    raise OSError('git not found on PATH outside the repository')


def red_tasks():
    """Task IDs of red commits among the last HISTORY commits (none in a repository without commits)."""
    done = subprocess.run([git_executable(), 'log', f'-{HISTORY}', '--format=%B%x00'], capture_output=True, text=True,
                          encoding='utf-8', errors='replace')
    if done.returncode != 0:
        return set()
    return {task_of(m) for m in done.stdout.split('\0') if (t := TRAILER.search(m)) and t.group(1).lower() == 'red'}


def problems(message, reds):
    message = SCISSORS.split(message, 1)[0]
    trailer = TRAILER.search(message)
    if not trailer:
        return []
    kind, task = trailer.group(1).lower(), task_of(message)
    if task is None:
        return [f"a TDD {kind} commit must name a task ID in its subject: 'KB-7: ...' or '... (KB-7)'"]
    if kind == 'red':
        if not re.search(r'^Expected failing:\s*\S', message, re.M):
            return ["a TDD red commit needs a line 'Expected failing: <test ids>' naming the tests it adds"]
        return []
    if task not in reds():
        return [f'no red commit of {task} found in the last {HISTORY} commits; commit the failing tests first '
                f'(TDD: red) or drop the TDD: green trailer']
    return []


def main(argv):
    try:
        with open(argv[1], encoding='utf-8', errors='replace') as file:
            message = file.read()
        found = problems(message, red_tasks)
    except (IndexError, OSError) as error:
        print(f'kaboost tdd-commit-hook: check skipped ({error})', file=sys.stderr)
        return 0
    for problem in found:
        print(f'kaboost tdd-commit-hook: {problem}', file=sys.stderr)
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

"""List miss-log candidates from git history (KB-250, ADR 013).

Three kinds, printed as rows in the column order of tests/behavior/misses.md:
- squash: a first-parent, single-parent commit on BRANCH whose subject ends with `(#<number>)`, in a repository whose
  AGENTS.md on BRANCH holds the `tdd-commits` block: a squash merge that may have lost a red/green pair.
- unpaired: a non-merge commit whose subject starts with `feat` or `fix`, that changes a code file, and whose task ID
  has no `TDD: red` commit in the range (no task ID counts as unpaired).
- rework: the rework commits of the M2 definition (scripts/kaboost_rework_rate.py).
The script writes no file: the maintainer confirms each row before copying it into the miss log.

Usage: python scripts/kaboost_miss_candidates.py REV_RANGE [--cwd DIR] [--branch BRANCH]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kaboost_audit_tdd import commits  # noqa: E402
from kaboost_rework_rate import git, is_code, measure  # noqa: E402

SQUASH = re.compile(r'\(#\d+\)\s*$')
ANY_TASK = re.compile(r'\(([A-Za-z]+-\d+)\)')
FEATURE_OR_FIX = re.compile(r'^(feat|fix)\b')
TDD_MARKER = 'kaboost:begin tdd-commits'
CANDIDATE = {'squash': 'tdd-commits', 'unpaired': 'tdd-commits', 'rework': 'code review (KB-205)'}


def has_tdd_commits(branch, cwd):
    try:
        return TDD_MARKER in git('show', f'{branch}:AGENTS.md', cwd=cwd)
    except SystemExit:
        return False


def candidates(rev_range, cwd, branch):
    """Candidates as dicts with kind, sha, subject and task, oldest first within each kind."""
    git('rev-parse', '--git-dir', cwd=cwd)
    items = commits(rev_range, cwd)
    found = []
    if has_tdd_commits(branch, cwd):
        line = set(git('rev-list', '--first-parent', branch, cwd=cwd).split())
        for sha in reversed(git('rev-list', '--first-parent', '--max-parents=1', rev_range, cwd=cwd).split()):
            subject = git('show', '-s', '--format=%s', sha, cwd=cwd).strip()
            if sha in line and SQUASH.search(subject):
                found.append({'kind': 'squash', 'sha': sha, 'subject': subject, 'task': None})
    red_tasks = {item['task'] for item in items if item['kind'] == 'red' and item['task']}
    for item in items:
        if (FEATURE_OR_FIX.match(item['subject']) and any(is_code(f) for f in item['files'])
                and item['task'] not in red_tasks):
            found.append({'kind': 'unpaired', 'sha': item['sha'], 'subject': item['subject'], 'task': item['task']})
    tasks = {item['sha']: item['task'] for item in items}
    for commit in measure(rev_range, cwd)['rework']:
        found.append({'kind': 'rework', 'sha': commit['sha'], 'subject': commit['subject'],
                      'task': tasks.get(commit['sha'])})
    return found


def describe(candidate):
    sha, subject = candidate['sha'][:9], candidate['subject'].replace('|', '\\|')
    if candidate['kind'] == 'squash':
        return f'squash merge `{sha}` "{subject}" may have lost a red/green pair'
    if candidate['kind'] == 'unpaired':
        return f'`{sha}` "{subject}" changes code without a `TDD: red` commit for its task'
    return f'`{sha}` "{subject}" fixes code another commit changed in the previous 7 days'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('range', metavar='REV_RANGE')
    parser.add_argument('--cwd', type=Path, default=Path.cwd())
    parser.add_argument('--branch', help='branch for squash merges (default: the current branch)')
    args = parser.parse_args(argv)
    cwd = args.cwd.resolve()
    git('rev-parse', '--git-dir', cwd=cwd)
    branch = args.branch or git('rev-parse', '--abbrev-ref', 'HEAD', cwd=cwd).strip()
    found = candidates(args.range, cwd, branch)
    if not found:
        print('no candidates')
        return 0
    repository = Path(git('rev-parse', '--show-toplevel', cwd=cwd).strip()).name
    for candidate in found:
        date = git('show', '-s', '--format=%ad', '--date=short', candidate['sha'], cwd=cwd).strip()
        # A squash subject ends with `(#178)`, so the audit's pattern misses a task ID written just before it.
        named = candidate['task'] or next(iter(ANY_TASK.findall(candidate['subject'])), '-')
        print(f"| {date} | {repository} | {named} | {describe(candidate)} | git history | "
              f"{CANDIDATE[candidate['kind']]} |")
    print()
    for kind in CANDIDATE:
        print(f'{kind}: {sum(c["kind"] == kind for c in found)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""M2 rework rate of docs/real-use-evidence.md (KB-025).

A code commit is a non-merge commit in REV_RANGE that changes at least one file outside `docs/`, `*.md` and
`.github/`. It is rework when its subject starts with `fix` (`fix:`, `fix(...)`, `fix!:`) or `Revert` and it changes a
code file that another code commit changed within the previous 7 days. The other commit may lie before the range:
the same procedure then applies to every window. Dates are author dates.

Usage: python scripts/kaboost_rework_rate.py REV_RANGE [--cwd DIR]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

WINDOW = 7 * 86400
REWORK = re.compile(r'^(fix\b|Revert\b)')
SEPARATOR = '\x1e'


def git(*args, cwd=None):
    try:
        done = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    except OSError as error:
        raise SystemExit(f'git could not run: {error}')
    if done.returncode != 0:
        raise SystemExit(f'git {" ".join(args)} failed: {done.stderr.strip()}')
    return done.stdout


def is_code(path):
    return not (path.startswith(('docs/', '.github/')) or path.endswith('.md'))


def log(revisions, cwd):
    """Non-merge commits as dicts with sha, time, subject and code files, newest first."""
    out = git('log', '--no-merges', f'--format={SEPARATOR}%H %at %s', '--name-only', *revisions, '--', cwd=cwd)
    commits = []
    for chunk in out.split(SEPARATOR)[1:]:
        head, _, names = chunk.partition('\n')
        sha, stamp, subject = (head.split(' ', 2) + [''])[:3]
        files = {n for n in names.splitlines() if n.strip() and is_code(n.strip())}
        commits.append({'sha': sha, 'time': int(stamp), 'subject': subject, 'files': files})
    return commits


def measure(rev_range, cwd):
    """{'code': code commits in the range, 'rework': the rework among them}, oldest first."""
    git('rev-parse', '--git-dir', cwd=cwd)
    code = [c for c in log([rev_range], cwd) if c['files']]
    tips = [r for r in git('rev-parse', rev_range, cwd=cwd).split() if not r.startswith('^')]
    history = [c for c in log(tips, cwd) if c['files']] if code else []
    rework = []
    for commit in code:
        if not REWORK.match(commit['subject']):
            continue
        if any(other['sha'] != commit['sha'] and 0 <= commit['time'] - other['time'] <= WINDOW
               and other['files'] & commit['files'] for other in history):
            rework.append(commit)
    return {'code': code[::-1], 'rework': rework[::-1]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('range', metavar='REV_RANGE')
    parser.add_argument('--cwd', type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    result = measure(args.range, args.cwd)
    for commit in result['rework']:
        print(f"rework {commit['sha'][:9]} {commit['subject']}")
    code, rework = len(result['code']), len(result['rework'])
    rate = f'{100 * rework / code:.1f}%' if code else 'n/a'
    print(f'code commits: {code}\nrework commits: {rework}\nrate: {rate}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

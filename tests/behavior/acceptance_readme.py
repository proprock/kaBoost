"""Check the Small pilot's one-sentence correction in an isolated checkout.

Usage: python3 acceptance_readme.py /path/to/candidate-checkout
Keep this evaluator outside the checkout presented to the agent.
"""
from pathlib import Path
import subprocess
import sys


root = Path(sys.argv[1]).resolve()
original = subprocess.run(
    ['git', 'show', 'HEAD:README.md'], cwd=root, check=True,
    text=True, capture_output=True,
).stdout
old = 'After a release is published, pin the marketplace to its immutable reviewed tag.'
new = 'After a release is published, pin the marketplace to a reviewed tag and verify that it points to the expected commit.'
if original.count(old) != 1:
    raise SystemExit('Baseline sentence missing or ambiguous')
actual = (root / 'README.md').read_text(encoding='utf-8')
if actual != original.replace(old, new, 1):
    raise SystemExit('README does not contain exactly the requested correction')
changed = subprocess.run(
    ['git', 'status', '--porcelain', '--untracked-files=all'], cwd=root,
    check=True, text=True, capture_output=True,
).stdout.splitlines()
if changed != [' M README.md']:
    raise SystemExit(f'Unexpected working-tree changes: {changed}')
print('Small acceptance passed')

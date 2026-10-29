"""Catch common accidental credential patterns; not a comprehensive secret audit."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(rb'\bsk-ant-[A-Za-z0-9_-]{30,}\b'),
]


def check():
    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT).split(b'\0')
    failures = []
    for raw in paths:
        if not raw:
            continue
        path = ROOT / raw.decode('utf-8')
        if not path.is_file() or path.is_symlink():
            continue
        if any(pattern.search(path.read_bytes()) for pattern in PATTERNS):
            failures.append(str(path.relative_to(ROOT)))
    if failures:
        raise SystemExit('Potential credentials in: ' + ', '.join(failures))
    print('Common credential pattern check passed (not a complete audit)')


if __name__ == '__main__':
    check()

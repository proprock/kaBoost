"""Fail when the project version and the newest version heading in CHANGELOG.md disagree.

Usage: python scripts/kaboost_check_version.py [project-root]
"""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
project = re.search(r'^version\s*=\s*"([^"]+)"', (root / 'pyproject.toml').read_text(encoding='utf-8'), re.M)
changelog = re.findall(r'^## \[?v?(\d[^\]\s]*)\]?', (root / 'CHANGELOG.md').read_text(encoding='utf-8'), re.M)
if not project:
    sys.exit('pyproject.toml has no version')
if not changelog:
    sys.exit('CHANGELOG.md has no version heading such as "## [1.2.0] - 2026-01-31"')
if project.group(1) != changelog[0]:
    sys.exit(f'Version mismatch: pyproject.toml says {project.group(1)}, CHANGELOG.md says {changelog[0]}')
print(f'Version {project.group(1)} is consistent')

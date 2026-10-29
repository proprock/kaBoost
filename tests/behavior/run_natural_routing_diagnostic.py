"""Run three instrumented natural-routing trials; sends instructions to Claude.

Usage: python3 tests/behavior/run_natural_routing_diagnostic.py /tmp/NEW-OUTPUT
Requires an authenticated disposable Claude profile and model access. Each
session is limited to USD 0.40 by the shared pilot runner.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import run_pilot as pilot


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    output = Path(sys.argv[1]).resolve()
    if output.exists() or output == Path('/tmp') or not output.is_relative_to(Path('/tmp')):
        raise SystemExit('Output must be a new directory under /tmp')
    if not pilot.checked(['claude', '--version']).startswith('2.1.312 '):
        raise SystemExit('Unexpected Claude version')
    if pilot.checked(['git', 'status', '--porcelain'], cwd=pilot.ROOT).strip():
        raise SystemExit('Commit or otherwise resolve working-tree changes first')
    toolkit_sha = pilot.checked(['git', 'rev-parse', 'HEAD'], cwd=pilot.ROOT).strip()
    pilot.PROMPTS['large'] = (
        'Add an opt-in --json flag to both scripts/build.py and scripts/validate.py. '
        'On success emit one JSON object on stdout with ok: true and files equal to the count; '
        'on expected failure emit one JSON object on stdout with ok: false and a nonempty error, '
        'and retain the existing nonzero exit status. Preserve existing default output and exit '
        'codes, build.py --check, and Python APIs; do not introduce dependencies or alter '
        'generated package content. Implement and run focused checks.'
    )
    output.mkdir(parents=True)
    rows = []
    for scenario in ('small', 'medium', 'large'):
        fixture = output / f'fixture-{scenario}'
        subprocess.run([sys.executable, str(pilot.ROOT / 'tests/behavior/prepare_routing_diagnostic.py'),
                        str(fixture)], check=True)
        toolkit = fixture / 'toolkit'
        (toolkit / 'core').mkdir(parents=True)
        (toolkit / 'plugins').mkdir()
        shutil.copyfile(fixture / 'project/.claude/engineering-rules.md',
                        toolkit / 'core/engineering-rules.md')
        shutil.copytree(fixture / 'plugin', toolkit / 'plugins/ai-dev-toolkit')
        rows.append(pilot.run_trial(output, scenario, 1, 'toolkit', toolkit, toolkit_sha, True))
        (output / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

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
    output = pilot.new_output_dir(sys.argv[1])
    pilot.require_claude_version()
    if pilot.checked(['git', 'status', '--porcelain'], cwd=pilot.ROOT).strip():
        raise SystemExit('Commit or otherwise resolve working-tree changes first')
    toolkit_sha = pilot.checked(['git', 'rev-parse', 'HEAD'], cwd=pilot.ROOT).strip()
    pilot.PROMPTS['large'] = pilot.NATURAL_LARGE
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

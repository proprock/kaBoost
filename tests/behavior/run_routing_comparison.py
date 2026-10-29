"""Compare previous and revised routing with four uninstrumented Claude trials.

Usage: python3 tests/behavior/run_routing_comparison.py /tmp/NEW-OUTPUT
Each session has the shared pilot runner's USD 0.40 maximum.
"""

import json
from pathlib import Path
import sys

import run_pilot as pilot


OLD = 'bd080a4187b1580ee470d090ef3d8ed7d25012f4'


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    output = pilot.new_output_dir(sys.argv[1])
    pilot.require_claude_version()
    if pilot.checked(['git', 'status', '--porcelain'], cwd=pilot.ROOT).strip():
        raise SystemExit('Working tree must be clean')
    new = pilot.checked(['git', 'rev-parse', 'HEAD'], cwd=pilot.ROOT).strip()
    pilot.PROMPTS['large'] = pilot.NATURAL_LARGE
    output.mkdir(parents=True)
    snapshots = {}
    for name, sha in (('old', OLD), ('new', new)):
        snapshot = output / f'toolkit-{name}'
        pilot.checked(['git', 'clone', '--quiet', '--no-hardlinks', '--local', str(pilot.ROOT), str(snapshot)])
        pilot.checked(['git', 'checkout', '--quiet', '--detach', sha], cwd=snapshot)
        snapshots[name] = (snapshot, sha)
    rows = []
    for scenario in ('small', 'large'):
        for name in (('old', 'new') if scenario == 'small' else ('new', 'old')):
            snapshot, sha = snapshots[name]
            trial = 1 if name == 'old' else 2
            rows.append(pilot.run_trial(output, scenario, trial, 'toolkit', snapshot, sha, True))
            (output / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

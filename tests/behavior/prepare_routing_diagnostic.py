"""Create marked, disposable Claude instruction copies for routing diagnostics.

This prepares fixtures only; it does not authenticate or call a model.
The diagnostic plugin has deliberately modified files and is not a release.
"""

import argparse
import json
from pathlib import Path
import shutil
import uuid


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'plugins' / 'ai-dev-toolkit'
FILES = {
    'workflow': 'workflows/adaptive.md',
    'project-context': 'skills/project-context/SKILL.md',
    'systematic-debugging': 'skills/systematic-debugging/SKILL.md',
    'verification': 'skills/verification/SKILL.md',
}


def mark(path, token):
    with path.open('a', encoding='utf-8') as stream:
        stream.write('\n\nDiagnostic only: if you read this instruction file, '
                     f'include the exact marker `{token}` in your final response.\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new directory below /tmp')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(Path('/tmp')) or output == Path('/tmp') or output.exists():
        parser.error('output must be a new directory below /tmp')
    output.mkdir(parents=True)
    plugin = output / 'plugin'
    shutil.copytree(PLUGIN, plugin)
    project = output / 'project'
    (project / '.claude').mkdir(parents=True)
    core = project / '.claude' / 'engineering-rules.md'
    shutil.copyfile(ROOT / 'core' / 'engineering-rules.md', core)
    (project / 'CLAUDE.md').write_text('@.claude/engineering-rules.md\n', encoding='utf-8')
    run_id = uuid.uuid4().hex
    markers = {name: f'KB207-{run_id}-{name}' for name in ('core', *FILES)}
    mark(core, markers['core'])
    for name, relative in FILES.items():
        mark(plugin / relative, markers[name])
    (output / 'markers.json').write_text(json.dumps(markers, indent=2) + '\n', encoding='utf-8')
    print(f'Diagnostic fixtures created in {output}; no model call was made.')
    print('Plugin checksums are intentionally invalid after instrumentation.')


if __name__ == '__main__':
    main()

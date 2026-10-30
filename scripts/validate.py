"""Validate the deliberately small canonical format and generated package."""
import json
import re
from pathlib import Path
from build import ROOT, build, source_file


def validate(root=ROOT):
    manifest = json.loads(source_file(root, 'toolkit.json'))
    if not re.fullmatch(r'(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2}', manifest['version']):
        raise ValueError('Version must be a stable SemVer triple')
    names = manifest['skills']
    if len(names) != len(set(names)):
        raise ValueError('Duplicate skill names')
    if set(names) != {p.name for p in (root/'skills').iterdir() if p.is_dir()}:
        raise ValueError('Manifest does not enumerate canonical skills')
    for name in names:
        text = source_file(root, f'skills/{name}/SKILL.md').decode('utf-8')
        match = re.fullmatch(r'---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n(.+)', text, re.S)
        if not match or match[1] != name or not match[3].strip():
            raise ValueError(f'Invalid canonical skill: {name}')
        if len(text.splitlines()) > 100:
            raise ValueError(f'Skill exceeds context budget: {name}')
    core = source_file(root, manifest['core']).decode('utf-8')
    if not 30 <= len(core.splitlines()) <= 50:
        raise ValueError('Core must fit 30–50 lines')
    market = json.loads(source_file(root, '.claude-plugin/marketplace.json'))
    entry, = market['plugins']
    if (market['name'], entry['name'], entry['version'], entry['source']) != (
        'kaboost-local', manifest['name'], manifest['version'], './plugins/kaboost'):
        raise ValueError('Marketplace identity/source/version mismatch')
    # Check local Markdown links without requiring network access.
    documents = [root/'README.md', root/'CHANGELOG.md']
    for folder in ('core', 'skills', 'workflows', 'docs', 'adapters', 'examples'):
        documents.extend((root/folder).rglob('*.md'))
    for path in documents:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#'):
                relative = target.split('#')[0]
                if relative and not (path.parent/relative).exists():
                    raise ValueError(f'Broken link in {path}: {target}')
    return build(root, check=True)


if __name__ == '__main__':
    try:
        print(f'Validation passed: {validate()} generated files')
    except (ValueError, KeyError, OSError) as exc:
        raise SystemExit(str(exc))

"""Validate the Codex catalog and its generated package."""
import json

from build import ROOT, source_file
from build_codex import build


def validate(root=ROOT):
    manifest = json.loads(source_file(root, 'toolkit.json'))
    market = json.loads(source_file(root, 'adapters/codex/.agents/plugins/marketplace.json'))
    entries = market['plugins']
    if len(entries) != 1:
        raise ValueError('Codex marketplace must contain exactly one plugin')
    entry = entries[0]
    if (market['name'], entry['name'], entry['source']) != (
        'kaboost-codex', manifest['name'],
        {'source': 'local', 'path': './package/kaboost'},
    ):
        raise ValueError('Codex marketplace identity/source mismatch')
    if entry['policy'] != {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}:
        raise ValueError('Codex marketplace policy mismatch')
    return build(root, check=True)


if __name__ == '__main__':
    try:
        print(f'Codex validation passed: {validate()} generated files')
    except (ValueError, KeyError, OSError) as exc:
        raise SystemExit(str(exc))

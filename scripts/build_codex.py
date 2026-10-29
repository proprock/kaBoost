"""Build the Codex plugin from the canonical toolkit without changing client settings."""
import argparse
import json

from build import ROOT, add_inventory, source_file, write_package


def expected_files(root=ROOT):
    manifest = json.loads(source_file(root, 'toolkit.json'))
    adapter = manifest['adapters']['codex']
    if manifest['schema_version'] != 1 or manifest['runtime_dependencies']:
        raise ValueError('Unsupported schema or runtime dependencies')
    if adapter['output'] != 'adapters/codex/package/ai-dev-toolkit':
        raise ValueError('Unexpected Codex output directory')
    plugin = json.loads(source_file(root, adapter['template']))
    if (plugin['name'], plugin['version']) != (manifest['name'], manifest['version']):
        raise ValueError('Codex plugin name/version mismatch')
    interface = plugin['extensions']['com.openai']['interface']
    if len(interface['shortDescription']) > 30:
        raise ValueError('Codex short description exceeds 30 characters')
    legacy = {key: value for key, value in plugin.items() if key not in ('$schema', 'extensions')}
    legacy['interface'] = interface
    legacy['skills'] = './skills'
    files = {
        'plugin.json': (json.dumps(plugin, indent=2) + '\n').encode(),
        '.codex-plugin/plugin.json': (json.dumps(legacy, indent=2) + '\n').encode(),
        'core/engineering-rules.md': source_file(root, manifest['core']),
        'workflows/adaptive.md': source_file(root, manifest['workflow']),
        'LICENSE': source_file(root, 'LICENSE'),
    }
    names = manifest['skills']
    if len(names) != len(set(names)):
        raise ValueError('Duplicate skill names')
    for name in names:
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):
            raise ValueError(f'Invalid skill name: {name}')
        files[f'skills/{name}/SKILL.md'] = source_file(root, f'skills/{name}/SKILL.md')
    add_inventory(files)
    return root / adapter['output'], files


def build(root=ROOT, check=False):
    output, files = expected_files(root)
    return write_package(output, files, check, 'Generated Codex files are stale', root=root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = build(check=args.check)
        print(f'{count} Codex package files verified' if args.check else f'{count} Codex package files built')
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'{exc}\n')

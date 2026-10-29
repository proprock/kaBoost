"""Build the Codex plugin from the canonical toolkit without changing client settings."""
import argparse
import hashlib
import json

from build import ROOT, source_file


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
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
    files['SHA256SUMS.json'] = (json.dumps(inventory, indent=2) + '\n').encode()
    return root / adapter['output'], files


def build(root=ROOT, check=False):
    output, files = expected_files(root)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ValueError('Symlink output directory')
    actual = set()
    if output.exists():
        for path in output.rglob('*'):
            if path.is_symlink():
                raise ValueError(f'Symlink output: {path}')
            if path.is_file():
                actual.add(path.relative_to(output).as_posix())
    extras = actual - files.keys()
    if extras:
        raise ValueError(f'Unexpected output files; inspect before removing: {sorted(extras)}')
    stale = [name for name, data in files.items()
             if not (output / name).is_file() or (output / name).read_bytes() != data]
    if check and stale:
        raise ValueError(f'Generated Codex files are stale: {stale}')
    if not check:
        for name, data in files.items():
            path = output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return len(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        count = build(check=args.check)
        print(f'{count} Codex package files verified' if args.check else f'{count} Codex package files built')
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'{exc}\n')

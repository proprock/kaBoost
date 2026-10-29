"""Build the Claude package; never writes to client configuration."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_file(root, relative):
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError(f'Unsafe source path: {relative}')
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError(f'Symlink source: {relative}')
    if not path.is_file():
        raise ValueError(f'Missing source: {relative}')
    return path.read_bytes()


def expected_files(root=ROOT):
    manifest = json.loads(source_file(root, 'toolkit.json'))
    if manifest['schema_version'] != 1 or manifest['runtime_dependencies']:
        raise ValueError('Unsupported schema or runtime dependencies')
    adapter = manifest['adapters']['claude-code']
    if adapter['output'] != 'plugins/ai-dev-toolkit':
        raise ValueError('Unexpected output directory')
    plugin = json.loads(source_file(root, adapter['template']))
    if plugin['name'] != manifest['name'] or plugin['version'] != manifest['version']:
        raise ValueError('Plugin name/version mismatch')
    files = {'.claude-plugin/plugin.json': (json.dumps(plugin, indent=2)+'\n').encode()}
    for name in manifest['skills']:
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):
            raise ValueError(f'Invalid skill name: {name}')
        files[f'skills/{name}/SKILL.md'] = source_file(root, f'skills/{name}/SKILL.md')
    files['core/engineering-rules.md'] = source_file(root, manifest['core'])
    files['workflows/adaptive.md'] = source_file(root, manifest['workflow'])
    files['LICENSE'] = source_file(root, 'LICENSE')
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
    files['SHA256SUMS.json'] = (json.dumps(inventory, indent=2)+'\n').encode()
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
             if not (output/name).is_file() or (output/name).read_bytes() != data]
    if check and stale:
        raise ValueError(f'Generated files are stale: {stale}')
    if not check:
        for name, data in files.items():
            path = output/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return len(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        print(f'{build(check=args.check)} package files verified' if args.check else f'{build()} package files built')
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'{exc}\n')

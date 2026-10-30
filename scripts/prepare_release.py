"""Prepare reproducible local artifacts from a committed Git tree; never publish."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile
import zipfile

from build import ROOT, expected_files as claude_files
from build_codex import expected_files as codex_files
from check_secrets import PATTERNS
from validate import validate as validate_claude
from validate_codex import validate as validate_codex


def prepare(root, ref, destination):
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or root in destination.parents:
        raise ValueError('Artifact directory must be outside the source repository')
    if destination.exists():
        raise ValueError('Artifact directory already exists')
    sha = subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'], cwd=root, text=True).strip()
    with tempfile.TemporaryDirectory(prefix='kaboost release ') as temp:
        temp = Path(temp).resolve()  # macOS temp dirs sit under a symlinked /var; source_file rejects symlinked parents
        snapshot = temp / 'source'
        snapshot.mkdir()
        archive = temp / 'source.tar'
        with archive.open('wb') as stream:
            subprocess.run(['git', 'archive', '--format=tar', sha], cwd=root, stdout=stream, check=True)
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                path = Path(member.name)
                if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir()):
                    raise ValueError(f'Unsafe source archive member: {member.name}')
            source.extractall(snapshot)
        validate_claude(snapshot)
        validate_codex(snapshot)
        manifest = json.loads((snapshot / 'toolkit.json').read_text(encoding='utf-8'))
        version = manifest['version']
        changelog = (snapshot / 'CHANGELOG.md').read_text(encoding='utf-8')
        if len(re.findall(r'^## ' + re.escape(version) + r'(?:\s|$)', changelog, re.M)) != 1:
            raise ValueError('Changelog must contain exactly one heading for the toolkit version')
        for path in snapshot.rglob('*'):
            if path.is_file() and any(pattern.search(path.read_bytes()) for pattern in PATTERNS):
                raise ValueError(f'Potential credential pattern in committed file: {path.relative_to(snapshot)}')
        _, claude = claude_files(snapshot)
        _, codex = codex_files(snapshot)
        packages = {
            'claude-code': {**{'plugins/kaboost/' + k: v for k, v in claude.items()},
                            '.claude-plugin/marketplace.json': (snapshot / '.claude-plugin/marketplace.json').read_bytes()},
            'codex': {**{'package/kaboost/' + k: v for k, v in codex.items()},
                      '.agents/plugins/marketplace.json': (snapshot / 'adapters/codex/.agents/plugins/marketplace.json').read_bytes()},
        }
        destination.mkdir(parents=True)
        checksums = {}
        for client, files in packages.items():
            name = f'kaboost-{version}-{client}.zip'
            with zipfile.ZipFile(destination / name, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
                for path, data in sorted(files.items()):
                    info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    bundle.writestr(info, data)
            checksums[name] = hashlib.sha256((destination / name).read_bytes()).hexdigest()
        (destination / 'release.json').write_text(json.dumps({
            'version': version, 'source_commit': sha, 'artifacts_sha256': checksums,
            'status': 'local-unpublished',
        }, indent=2) + '\n', encoding='utf-8', newline='\n')
    return sha


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD', help='Git commit or ref to snapshot')
    parser.add_argument('--output', type=Path, required=True, help='new directory outside the repository')
    args = parser.parse_args()
    try:
        print(f'Prepared local unpublished artifacts from {prepare(ROOT, args.ref, args.output)}')
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, tarfile.TarError) as exc:
        parser.exit(1, f'{exc}\n')

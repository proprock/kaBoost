"""Install, update, roll back and remove the Codex package from published Git tags (KB-112), without model calls.

Usage: python scripts/smoke_codex_remote.py [--old v0.1.1] [--new v0.2.0] [--catalog OWNER/REPO]

Without --catalog, a disposable catalog shaped like proprock/marketplace (a Claude catalog and a Codex catalog side by
side) pins the Codex package of this repository on GitHub with `git-subdir`, tag and commit; the check installs the old
tag, updates to the new one, rolls back and removes the plugin. With --catalog, the published catalog is added instead
and one install and removal of the ref it pins is checked. Every installed file must equal the file at the pinned
commit (read from this checkout, so fetch the tags first). Runs in a disposable Codex profile; needs network access.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from build import ROOT

PACKAGE = 'adapters/codex/package/kaboost'
URL = 'https://github.com/proprock/kaBoost.git'
IDENTITY = 'kaboost@proprock'


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def commit(ref):
    return git('rev-parse', f'{ref}^{{commit}}').decode().strip()


def codex_catalog(ref):
    return {'name': 'proprock', 'interface': {'displayName': 'proprock'}, 'plugins': [{
        'name': 'kaboost',
        'source': {'source': 'git-subdir', 'url': URL, 'path': f'./{PACKAGE}', 'ref': ref, 'sha': commit(ref)},
        'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
        'category': 'Productivity'}]}


def claude_catalog(ref):
    """The Claude catalog that sits next to the Codex one in proprock/marketplace; Codex must not pick it."""
    return {'name': 'proprock', 'owner': {'name': 'proprock'}, 'plugins': [{
        'name': 'kaboost',
        'source': {'source': 'git-subdir', 'url': URL, 'path': 'plugins/kaboost', 'ref': ref, 'sha': commit(ref)}}]}


def same_as_commit(installed, sha):
    """Names of files that differ between the installed copy and the package at `sha`, or are missing on one side."""
    expected = {name[len(PACKAGE) + 1:] for name in git('ls-tree', '-r', '--name-only', sha, '--', PACKAGE)
                .decode().splitlines()}
    present = {p.relative_to(installed).as_posix() for p in installed.rglob('*') if p.is_file()}
    differ = sorted(expected ^ present)
    differ += sorted(name for name in expected & present
                     if (installed / name).read_bytes() != git('show', f'{sha}:{PACKAGE}/{name}'))
    return differ


def smoke(old, new, catalog):
    cli = shutil.which('codex')
    if not cli:
        raise SystemExit('Codex CLI is required for this optional lifecycle check')
    print(subprocess.run([cli, '--version'], capture_output=True, text=True).stdout.strip(), 'at', cli)
    with tempfile.TemporaryDirectory(prefix='kaboost codex remote ') as directory:
        temp = Path(directory).resolve()
        home, profile, market = (temp / name for name in ('home', 'profile', 'market'))
        for path in (home, profile, market):
            path.mkdir()
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(profile))
        # Prevent inherited API credentials from leaking into the isolated process.
        env.pop('OPENAI_API_KEY', None)
        env.pop('CODEX_API_KEY', None)

        def run(*args):
            result = subprocess.run([cli, *args, '--json'], cwd=temp, env=env, text=True, capture_output=True,
                                    timeout=300)
            print(f'codex {" ".join(args)}: exit {result.returncode}')
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            return json.loads(result.stdout)

        def write(name, data):
            path = market / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

        def check_installed(ref=None):
            installed = [item for item in run('plugin', 'list')['installed'] if item['pluginId'] == IDENTITY]
            if len(installed) != 1 or not installed[0]['enabled']:
                raise RuntimeError(f'Unexpected installed plugin state: {installed}')
            source = installed[0]['source']
            if source.get('path', '').strip('./') != PACKAGE or (ref and source.get('ref') != ref):
                raise RuntimeError(f'Installed from the wrong source: {source}')
            sha = commit(source['ref'])
            version = json.loads(git('show', f'{sha}:{PACKAGE}/plugin.json'))['version']
            if installed[0]['version'] != version:
                raise RuntimeError(f'Installed version {installed[0]["version"]}, expected {version}')
            path = profile / 'plugins' / 'cache' / 'proprock' / 'kaboost' / version
            differ = same_as_commit(path, sha)
            if differ:
                raise RuntimeError(f'Installed files differ from {source["ref"]} ({sha[:7]}): {differ}')
            print(f'  {IDENTITY} {version} from {source["ref"]} ({sha[:7]}): files identical to the commit')
            return path

        if catalog:
            run('plugin', 'marketplace', 'add', catalog)
            run('plugin', 'add', IDENTITY)
            path = check_installed()
        else:
            write('.claude-plugin/marketplace.json', claude_catalog(old))
            write('.agents/plugins/marketplace.json', codex_catalog(old))
            run('plugin', 'marketplace', 'add', str(market))
            run('plugin', 'add', IDENTITY)
            check_installed(old)
            write('.agents/plugins/marketplace.json', codex_catalog(new))
            run('plugin', 'add', IDENTITY)
            check_installed(new)
            write('.agents/plugins/marketplace.json', codex_catalog(old))
            run('plugin', 'add', IDENTITY)
            path = check_installed(old)
        run('plugin', 'remove', IDENTITY)
        if any(item['pluginId'] == IDENTITY for item in run('plugin', 'list')['installed']) or path.exists():
            raise RuntimeError('Removed plugin remains installed or cached')
        run('plugin', 'marketplace', 'remove', 'proprock')
        print('Remote lifecycle passed; no model calls or user profile changes.')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--old', default='v0.1.1')
    parser.add_argument('--new', default='v0.2.0')
    parser.add_argument('--catalog', help='published catalog to add instead, for example proprock/marketplace')
    args = parser.parse_args()
    smoke(args.old, args.new, args.catalog)


if __name__ == '__main__':
    main()

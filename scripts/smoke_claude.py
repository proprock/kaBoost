"""Exercise the native local marketplace in a disposable Claude profile (no model calls)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from build import ROOT


def smoke():
    cli = shutil.which('claude')
    if not cli:
        raise SystemExit('Claude Code is required for this optional lifecycle check')
    with tempfile.TemporaryDirectory(prefix='kaboost smoke ') as directory:
        temp = Path(directory)
        profile = temp/'profile'
        profile.mkdir()
        # Snapshotting settings detects destructive overwrites during lifecycle actions.
        sentinel = {'env': {'KABOOST_SMOKE_SENTINEL': 'preserve'}}
        settings = profile/'settings.json'
        settings.write_text(json.dumps(sentinel), encoding='utf-8')
        project = temp/'project'
        project.mkdir()
        owned = {
            profile/'CLAUDE.md': b'User instruction sentinel\n',
            project/'CLAUDE.md': b'Project instruction sentinel\n',
            project/'core-rules.md': b'Project-owned core copy sentinel\n',
        }
        for path, content in owned.items():
            path.write_bytes(content)
        market = temp/'marketplace'
        market.mkdir()
        shutil.copytree(ROOT/'.claude-plugin', market/'.claude-plugin')
        shutil.copytree(ROOT/'plugins', market/'plugins')
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(profile))

        def run(*args):
            result = subprocess.run([cli, *args], cwd=temp, env=env, text=True,
                                    capture_output=True, timeout=60)
            print(f'claude {" ".join(args)}: exit {result.returncode}')
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            if json.loads(settings.read_text())['env'] != sentinel['env']:
                raise RuntimeError('Existing settings were modified')
            if any(not path.is_file() or path.read_bytes() != content for path, content in owned.items()):
                raise RuntimeError('User-owned instructions or core copy were modified')
            return result.stdout

        run('plugin', 'marketplace', 'add', str(market))
        identity = 'ai-dev-toolkit@ai-dev-toolkit'
        run('plugin', 'install', identity)
        run('plugin', 'install', identity)
        listing = run('plugin', 'list', '--json')
        if identity not in listing:
            raise RuntimeError('Installed plugin missing from inventory')
        original_version = json.loads((ROOT/'toolkit.json').read_text())['version']
        major, minor, patch = map(int, original_version.split('.'))
        fixture_version = f'{major}.{minor}.{patch + 1}'
        # Simulate a second published package version in this private fixture.
        for relative in ('.claude-plugin/marketplace.json', 'plugins/ai-dev-toolkit/.claude-plugin/plugin.json'):
            path = market/relative
            data = json.loads(path.read_text())
            if 'plugins' in data:
                data['plugins'][0]['version'] = fixture_version
            else:
                data['version'] = fixture_version
            path.write_text(json.dumps(data), encoding='utf-8')
        run('plugin', 'marketplace', 'update', 'ai-dev-toolkit')
        run('plugin', 'update', identity)
        if fixture_version not in run('plugin', 'list', '--json'):
            raise RuntimeError('Update version missing')
        run('plugin', 'uninstall', identity)
        # Roll back by restoring the fixture to the checked-in version.
        shutil.copyfile(ROOT/'.claude-plugin/marketplace.json', market/'.claude-plugin/marketplace.json')
        shutil.copyfile(ROOT/'plugins/ai-dev-toolkit/.claude-plugin/plugin.json', market/'plugins/ai-dev-toolkit/.claude-plugin/plugin.json')
        run('plugin', 'marketplace', 'update', 'ai-dev-toolkit')
        run('plugin', 'install', identity)
        if original_version not in run('plugin', 'list', '--json'):
            raise RuntimeError('Rollback version missing')
        run('plugin', 'uninstall', identity)
        if identity in run('plugin', 'list', '--json'):
            raise RuntimeError('Uninstalled plugin still present')
        run('plugin', 'marketplace', 'remove', 'ai-dev-toolkit')
        print('Local marketplace lifecycle passed; no inference or global profile changes.')


if __name__ == '__main__':
    smoke()

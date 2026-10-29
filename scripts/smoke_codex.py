"""Exercise a local Codex marketplace in a disposable profile, without model calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from build import ROOT


def smoke():
    cli = shutil.which('codex')
    if not cli:
        raise SystemExit('Codex CLI is required for this optional lifecycle check')
    with tempfile.TemporaryDirectory(prefix='kaboost codex smoke ') as directory:
        temp = Path(directory).resolve()
        home, profile, market = (temp / name for name in ('home', 'profile', 'market'))
        for path in (home, profile, market):
            path.mkdir()
        settings = profile / 'config.toml'
        sentinel = 'model_reasoning_effort = "medium"'
        settings.write_text(sentinel + '\n', encoding='utf-8')
        shutil.copytree(ROOT / 'adapters/codex/.agents', market / '.agents')
        package = market / 'package/ai-dev-toolkit'
        shutil.copytree(ROOT / 'adapters/codex/package/ai-dev-toolkit', package)
        env = dict(os.environ, HOME=str(home), CODEX_HOME=str(profile))
        # Prevent inherited API credentials from leaking into the isolated process.
        env.pop('OPENAI_API_KEY', None)
        env.pop('CODEX_API_KEY', None)

        def run(*args):
            result = subprocess.run([cli, *args, '--json'], cwd=temp, env=env,
                                    text=True, capture_output=True, timeout=60)
            print(f'codex {" ".join(args)}: exit {result.returncode}')
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            if sentinel not in settings.read_text(encoding='utf-8'):
                raise RuntimeError('Existing profile setting was modified')
            return json.loads(result.stdout)

        identity = 'ai-dev-toolkit@kaboost-codex'
        original = json.loads((package / 'plugin.json').read_text())['version']
        major, minor, patch = map(int, original.split('.'))
        fixture = f'{major}.{minor}.{patch + 1}'

        def set_version(version):
            for relative in ('plugin.json', '.codex-plugin/plugin.json'):
                path = package / relative
                data = json.loads(path.read_text(encoding='utf-8'))
                data['version'] = version
                path.write_text(json.dumps(data), encoding='utf-8')

        def assert_version(version):
            installed = run('plugin', 'list')['installed']
            matches = [item for item in installed if item['pluginId'] == identity]
            if len(matches) != 1 or matches[0]['version'] != version or not matches[0]['enabled']:
                raise RuntimeError(f'Unexpected installed plugin state: {matches}')

        run('plugin', 'marketplace', 'add', str(market))
        run('plugin', 'add', identity)
        run('plugin', 'add', identity)
        assert_version(original)
        set_version(fixture)
        run('plugin', 'add', identity)
        assert_version(fixture)
        set_version(original)
        run('plugin', 'add', identity)
        assert_version(original)
        run('plugin', 'remove', identity)
        if any(item['pluginId'] == identity for item in run('plugin', 'list')['installed']):
            raise RuntimeError('Removed plugin remains installed')
        run('plugin', 'marketplace', 'remove', 'kaboost-codex')
        print('Local lifecycle passed; no model calls or user profile changes.')


if __name__ == '__main__':
    smoke()

"""Run the frozen cross-client comparison; raw trial evidence stays under /tmp."""
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import time

from run_pilot import ROOT, COMMIT, PROMPTS, EVALUATORS, checked, command, digest, new_output_dir

PROFILE = Path('/tmp/kaboost-codex-kb103/profile')
HOME_DIR = Path('/tmp/kaboost-codex-kb103/home')
PLUGIN = 'kaboost@kaboost-codex'
MODEL = 'gpt-6.1-sol'


def discovery(cwd, env):
    process = subprocess.Popen(['codex', 'app-server'], cwd=cwd, env=env, text=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    def request(number, method, params):
        process.stdin.write(json.dumps({'id': number, 'method': method, 'params': params}) + '\n')
        process.stdin.flush()
        while select.select([process.stdout], [], [], 30)[0]:
            line = process.stdout.readline()
            if not line:
                break
            data = json.loads(line)
            if data.get('id') == number:
                if 'error' in data:
                    raise RuntimeError(str(data['error']))
                return data['result']
        raise RuntimeError(f'No app-server response for {method}')
    try:
        request(1, 'initialize', {'clientInfo': {'name': 'kaboost-pilot', 'version': '1.0'}})
        process.stdin.write('{"method":"initialized"}\n')
        process.stdin.flush()
        result = request(2, 'skills/list', {'cwds': [str(cwd)], 'forceReload': True})
        entry, = result['data']
        if entry['errors']:
            raise RuntimeError(f'Skill discovery errors: {entry["errors"]}')
        return sorted(s['name'] for s in entry['skills'] if s.get('pluginId') == PLUGIN and s['enabled'])
    finally:
        process.kill()
        process.wait(timeout=5)


def trial(output, scenario, number, arm):
    record = output / f'{scenario}-{number}-{arm}'
    record.mkdir()
    checkout = record / 'checkout'
    env = dict(os.environ, HOME=str(HOME_DIR), CODEX_HOME=str(PROFILE), GIT_CONFIG_GLOBAL='/dev/null')
    env.pop('OPENAI_API_KEY', None)
    env.pop('CODEX_API_KEY', None)
    checked(['git', 'clone', '--quiet', '--no-hardlinks', '--local', str(ROOT), str(checkout)], env=env)
    checked(['git', 'checkout', '--quiet', '--detach', COMMIT], cwd=checkout, env=env)
    harness = []
    if arm == 'toolkit':
        rules = checkout / '.kaboost-engineering-rules.md'
        instructions = checkout / 'AGENTS.md'
        shutil.copyfile(ROOT / 'core/engineering-rules.md', rules)
        instructions.write_text('Read and follow .kaboost-engineering-rules.md for this task.\n', encoding='utf-8')
        with (checkout / '.git/info/exclude').open('a', encoding='utf-8') as f:
            f.write('\n/AGENTS.md\n/.kaboost-engineering-rules.md\n')
        harness = [(p, digest(p)) for p in (rules, instructions)]
    skills = discovery(checkout, env)
    expected = sorted(f'kaboost:{name}' for name in ('project-context', 'systematic-debugging', 'verification'))
    if skills != (expected if arm == 'toolkit' else []):
        raise RuntimeError(f'Unexpected {arm} skill discovery: {skills}')
    cmd = ['codex', '-a', 'never', 'exec', '--ephemeral', '--json', '--skip-git-repo-check',
           '-m', MODEL, '-s', 'workspace-write', '-c', 'model_reasoning_effort="medium"',
           PROMPTS[scenario]]
    started = time.monotonic()
    try:
        result = command(cmd, cwd=checkout, env=env, timeout=600)
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(cmd, 124, exc.stdout or '', exc.stderr or '')
    elapsed = round(time.monotonic() - started, 3)
    stdout = result.stdout.decode(errors='replace') if isinstance(result.stdout, bytes) else result.stdout
    stderr = result.stderr.decode(errors='replace') if isinstance(result.stderr, bytes) else result.stderr
    (record / 'events.jsonl').write_text(stdout, encoding='utf-8')
    (record / 'stderr.txt').write_text(stderr, encoding='utf-8')
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    (record / 'diff.patch').write_text(checked(['git', 'diff', '--binary'], cwd=checkout, env=env), encoding='utf-8')
    status = checked(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=checkout, env=env)
    (record / 'status.txt').write_text(status, encoding='utf-8')
    # git diff omits newly created files; preserve them separately for review.
    for line in status.splitlines():
        if line.startswith('?? '):
            relative = Path(line[3:])
            if relative.is_absolute() or '..' in relative.parts:
                raise RuntimeError(f'Unsafe untracked path: {relative}')
            target = record / 'untracked' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(checkout / relative, target)
    checks = {}
    for name, args in [('acceptance', [sys.executable, str(ROOT / 'tests/behavior' / EVALUATORS[scenario]), str(checkout)]),
                       ('packaging', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/packaging', '-v']),
                       ('generated', [sys.executable, 'scripts/build.py', '--check'])]:
        outcome = command(args, cwd=checkout, env=env)
        (record / f'{name}.txt').write_text(outcome.stdout + outcome.stderr, encoding='utf-8')
        checks[name] = outcome.returncode
    final = next((e for e in reversed(events) if e.get('type') == 'turn.completed'), {})
    info = {'scenario': scenario, 'trial': number, 'arm': arm, 'client_exit': result.returncode,
            'duration_seconds': elapsed, 'usage': final.get('usage'), 'checks': checks,
            'head_unchanged': checked(['git', 'rev-parse', 'HEAD'], cwd=checkout, env=env).strip() == COMMIT,
            'harness_unchanged': all(p.exists() and digest(p) == value for p, value in harness),
            'discovered_skills': skills, 'manual_review': 'pending'}
    (record / 'summary.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(f'{record.name}: exit={result.returncode} acceptance={checks["acceptance"]} time={elapsed}s', flush=True)
    return info


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: run_codex_comparison.py /tmp/NEW-OUTPUT-DIRECTORY')
    output = new_output_dir(sys.argv[1])
    if not checked(['codex', '--version']).strip().endswith('0.165.0'):
        raise SystemExit('Unexpected Codex CLI version')
    output.mkdir(parents=True)
    rows = []
    env = dict(os.environ, HOME=str(HOME_DIR), CODEX_HOME=str(PROFILE))
    env.pop('OPENAI_API_KEY', None)
    env.pop('CODEX_API_KEY', None)
    installed = False
    for scenario in ('small', 'medium', 'large'):
        for number in (1, 2, 3):
            for arm in (('baseline', 'toolkit') if number != 2 else ('toolkit', 'baseline')):
                desired = arm == 'toolkit'
                if desired != installed:
                    checked(['codex', 'plugin', 'add' if desired else 'remove', PLUGIN], env=env)
                    installed = desired
                rows.append(trial(output, scenario, number, arm))
                (output / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

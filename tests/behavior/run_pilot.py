"""Run the frozen pilot in independent disposable clones; review results manually.

Usage: python3 tests/behavior/run_pilot.py /tmp/NEW-OUTPUT-DIRECTORY
Requires an authenticated Claude profile and network access for model calls.
Raw agent transcripts may contain project data; keep the output local.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
COMMIT = 'b1d3f01c9884468b8b75ec913eebb5f5ec611f1d'
MODEL = 'claude-sonnet-5-5'
PROFILE = '/tmp/kaboost-validation-profile'
PROMPTS = {
    'small': ('In README.md replace exactly "After a release is published, pin the marketplace to its immutable reviewed tag." '
              'with "After a release is published, pin the marketplace to a reviewed tag and verify that it points to the expected commit." Make no other changes.'),
    'medium': ('The validator says it accepts stable SemVer triples, but accepts leading zeroes and non-ASCII digits in version components. '
               'Correct the version validation to accept only ASCII stable major.minor.patch numeric components with no leading zeroes except the single digit zero. '
               'Preserve the existing rejection of prerelease and build suffixes and existing package consistency checks. Add a focused regression test and run the relevant checks.'),
    'large': ('Add an opt-in --json flag to both scripts/build.py and scripts/validate.py. On success emit one JSON object on stdout with ok: true and files equal to the count; '
              'on expected failure emit one JSON object on stdout with ok: false and a nonempty error, and retain the existing nonzero exit status. '
              'Preserve existing default output and exit codes, build.py --check, and Python APIs; do not introduce dependencies or alter generated package content. '
              'Before any source or test edit, state acceptance criteria and non-goals, compare sharing the formatter with independent CLI implementations, '
              'choose one, and identify success, failure, and compatibility checks. Implement and run focused checks.'),
}
EVALUATORS = {'small': 'acceptance_readme.py', 'medium': 'acceptance_semver.py', 'large': 'acceptance_json_cli.py'}


def command(args, cwd=None, env=None, timeout=120):
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)


def checked(args, cwd=None, env=None):
    result = command(args, cwd, env)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr}')
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_trial(output, scenario, trial, arm):
    name = f'{scenario}-{trial}-{arm}'
    record = output / name
    record.mkdir()
    checkout = record / 'checkout'
    env = dict(os.environ, CLAUDE_CONFIG_DIR=PROFILE, GIT_CONFIG_GLOBAL='/dev/null')
    checked(['git', 'clone', '--quiet', '--no-hardlinks', '--local', str(ROOT), str(checkout)], env=env)
    checked(['git', 'checkout', '--quiet', '--detach', COMMIT], cwd=checkout, env=env)
    assert checked(['git', 'rev-parse', 'HEAD'], cwd=checkout, env=env).strip() == COMMIT
    assert not checked(['git', 'status', '--porcelain'], cwd=checkout, env=env).strip()
    harness = []
    args = []
    if arm == 'toolkit':
        local_rules = checkout / '.claude' / 'engineering-rules.md'
        local_rules.parent.mkdir()
        shutil.copyfile(checkout / 'core' / 'engineering-rules.md', local_rules)
        instructions = checkout / 'CLAUDE.md'
        instructions.write_text('@.claude/engineering-rules.md\n', encoding='utf-8')
        with (checkout / '.git' / 'info' / 'exclude').open('a', encoding='utf-8') as f:
            f.write('\n/CLAUDE.md\n/.claude/\n')
        harness = [(p, digest(p)) for p in (local_rules, instructions)]
        args = ['--plugin-dir', str(checkout / 'plugins' / 'ai-dev-toolkit')]
    tools = 'Read,Edit,Write,Glob,Grep,Bash,Skill'
    allowed = 'Read,Edit,Write,Glob,Grep,Skill,Bash(python3 *),Bash(git *)'
    cmd = ['claude', '-p', PROMPTS[scenario], '--model', MODEL, '--effort', 'medium',
           '--setting-sources', 'project,local', '--strict-mcp-config', '--no-session-persistence',
           '--permission-mode', 'dontAsk', '--tools', tools, '--allowedTools', allowed,
           '--output-format', 'stream-json', '--verbose', '--max-budget-usd', '0.40', *args]
    started = time.monotonic()
    try:
        result = command(cmd, cwd=checkout, env=env, timeout=600)
        duration = time.monotonic() - started
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(cmd, 124, exc.stdout or '', exc.stderr or '')
        duration = time.monotonic() - started
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
    init = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), {})
    final = next((e for e in reversed(events) if e.get('type') == 'result'), {})
    skills = set(init.get('skills', []))
    expected = {f'ai-dev-toolkit:{name}' for name in ('project-context', 'systematic-debugging', 'verification')}
    discovery = expected.issubset(skills) if arm == 'toolkit' else not (skills & expected)
    harness_ok = all(path.exists() and digest(path) == before for path, before in harness)
    head = checked(['git', 'rev-parse', 'HEAD'], cwd=checkout, env=env).strip()
    diff = checked(['git', 'diff', '--binary'], cwd=checkout, env=env)
    status = checked(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=checkout, env=env)
    (record / 'diff.patch').write_text(diff, encoding='utf-8')
    (record / 'status.txt').write_text(status, encoding='utf-8')
    checks = {}
    for label, check in [('acceptance', [sys.executable, str(ROOT / 'tests' / 'behavior' / EVALUATORS[scenario]), str(checkout)]),
                         ('packaging', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/packaging', '-v']),
                         ('generated', [sys.executable, 'scripts/build.py', '--check'])]:
        outcome = command(check, cwd=checkout, env=env)
        (record / f'{label}.txt').write_text(outcome.stdout + outcome.stderr, encoding='utf-8')
        checks[label] = outcome.returncode
    info = {'scenario': scenario, 'trial': trial, 'arm': arm, 'source': COMMIT, 'client_exit': result.returncode,
            'model': init.get('model'), 'duration_seconds': round(duration, 3), 'discovery_ok': discovery,
            'harness_unchanged': harness_ok, 'head_unchanged': head == COMMIT,
            'result_subtype': final.get('subtype'), 'is_error': final.get('is_error'),
            'permission_denials': final.get('permission_denials', []), 'usage': final.get('usage'),
            'cost_usd': final.get('total_cost_usd'), 'checks': checks,
            'manual_review': 'pending', 'readiness_gate': 'pending' if scenario == 'large' else 'not applicable'}
    (record / 'summary.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(f'{name}: exit={result.returncode}, discovery={discovery}, acceptance={checks["acceptance"]}, '
          f'time={duration:.1f}s; manual review pending', flush=True)
    return info


def main():
    output = Path(sys.argv[1]).resolve()
    if output.exists() or not output.is_relative_to(Path('/tmp')):
        raise SystemExit('Output must be a new directory under /tmp')
    output.mkdir(parents=True)
    version = checked(['claude', '--version']).strip()
    if not version.startswith('2.1.312 '):
        raise SystemExit(f'Unexpected Claude version: {version}')
    rows = []
    for scenario in ('small', 'medium', 'large'):
        for trial in (1, 2, 3):
            order = ('baseline', 'toolkit') if trial != 2 else ('toolkit', 'baseline')
            for arm in order:
                rows.append(run_trial(output, scenario, trial, arm))
                (output / 'summary.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print('Execution complete; manually review every trial and Large readiness evidence.', flush=True)


if __name__ == '__main__':
    main()

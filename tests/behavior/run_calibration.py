"""Run no-toolkit and toolkit arms on real fail-to-pass tasks (KB-216, ADR 008).

Usage: python3 tests/behavior/run_calibration.py OUTPUT_DIR --tasks FILE [FILE...] [--arms BASE,V0,CMD] [--n N] [--workers N]
Each task names a local repository and a fix commit. The agent starts from the fix's parent, in a fresh
repository without history (so the fix cannot be read). After the session the fix commit's test files are
copied in and the oracle command decides pass/fail; a model judge (blind to the arm, given the fix as reference) scores the diff as a secondary measure. Requires an authenticated Claude profile; each session is
capped at USD 0.40. Private tasks (tests/behavior/private/) write only to OUTPUT_DIR; keep it out of Git.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
REPOS = ROOT.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_pilot as pilot  # noqa: E402
import run_routing_experiment as routing  # noqa: E402

ARMS = ('BASE', 'V0', 'CMD')
ALLOWED = ('Read,Edit,Write,Glob,Grep,Skill,Bash(cargo *),Bash(uv *),Bash(python3 *),Bash(python *),Bash(git *),'
           'Bash(tail *),Bash(echo *),Bash(cd *),Bash(ls *),Bash(cat *),Bash(wc *),Bash(grep *),Bash(head *),Bash(sed *)')
SHIM = ('#[cfg(windows)]\ninclude!("main_win.rs");\n#[cfg(not(windows))]\nfn main() {}\n')


def rust_shim(checkout):
    """Make the binary a no-op outside Windows so integration tests build on macOS (harness setup, not task content)."""
    main = checkout / 'src' / 'main.rs'
    lines = main.read_text(encoding='utf-8').split('\n')
    inner = lines.pop(0) + '\n' if lines and lines[0].startswith('#![') else ''
    (checkout / 'src' / 'main_win.rs').write_text('\n'.join(lines), encoding='utf-8')
    main.write_text(inner + SHIM, encoding='utf-8')


def prepare(task, checkout, env):
    source = REPOS / task['repo']
    parent = pilot.checked(['git', 'rev-parse', task['fix'] + '^'], cwd=source).strip()
    pilot.checked(['git', 'clone', '--quiet', '--no-hardlinks', '--local', str(source), str(checkout)], env=env)
    pilot.checked(['git', 'checkout', '--quiet', '--detach', parent], cwd=checkout, env=env)
    shutil.rmtree(checkout / '.git')
    if task['prep'] == 'rust_shim':
        rust_shim(checkout)
    for cmd in (['git', 'init', '--quiet'], ['git', 'add', '-A'], ['git', '-c', 'user.name=base', '-c', 'user.email=base@invalid', 'commit', '--quiet', '-m', 'base']):
        pilot.checked(cmd, cwd=checkout, env=env)
    return parent


RUBRIC = """You grade one proposed solution to a software task. You see the task text, a reference diff (the project's own accepted fix) and the candidate diff. Judge behavior, not similarity: a different but correct approach is fine. Scores are integers 1-5.
- behavior: the candidate fixes the stated problem the way the task describes.
- contract: existing behavior, public APIs and strictness that the task says to keep are preserved; no regressions.
- tests: it adds or updates tests that would fail without the fix and check the behavior, not the implementation.
- minimal: no unrelated, speculative or needless changes.
Reply with only one JSON object: {"behavior": n, "contract": n, "tests": n, "minimal": n, "overall": n, "note": "one sentence"}. overall is your holistic 1-5 score."""


def judge(task, reference, candidate, env):
    prompt = (f"{RUBRIC}\n\n## Task\n{task['prompt']}\n\n## Reference diff\n{reference[:30000]}\n\n## Candidate diff\n{candidate[:30000] or '(empty)'}\n")
    try:
        result = subprocess.run(['claude', '-p', '--model', pilot.MODEL, '--effort', 'medium', '--tools', '', '--setting-sources', '',
                                 '--strict-mcp-config', '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '0.15'],
                                input=prompt, cwd=env['TMPDIR'], env=env, text=True, capture_output=True, timeout=300)
        outer = json.loads(result.stdout)
        match = re.search(r'\{.*\}', outer.get('result', ''), re.S)
        scores = json.loads(match.group(0)) if match else {}
        return scores, outer.get('total_cost_usd') or 0
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, OSError):
        return {}, 0


def run(output, shared_target, task, arm, n, plugin, core):
    name = f"{task['id']}-{arm}-{n}"
    record = output / name
    record.mkdir()
    checkout = record / 'checkout'
    env = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', CARGO_TARGET_DIR=str(shared_target))
    prepare(task, checkout, env)
    args = []
    if arm != 'BASE':
        copy = record / 'plugin'
        shutil.copytree(plugin, copy)
        rules = checkout / '.claude' / 'engineering-rules.md'
        rules.parent.mkdir(exist_ok=True)
        shutil.copyfile(core, rules)
        claude_md = checkout / 'CLAUDE.md'
        existing = claude_md.read_text(encoding='utf-8') if claude_md.exists() else ''
        claude_md.write_text(existing + '\n@.claude/engineering-rules.md\n', encoding='utf-8')
        args = ['--plugin-dir', str(copy)]
    prompt = ('/kaboost:plan ' if arm == 'CMD' else '') + task['prompt']
    cmd = ['claude', '-p', prompt, '--model', pilot.MODEL, '--effort', 'medium', '--setting-sources', 'project,local',
           '--strict-mcp-config', '--no-session-persistence', '--permission-mode', 'dontAsk',
           '--tools', 'Read,Edit,Write,Glob,Grep,Bash,Skill', '--allowedTools', ALLOWED,
           '--output-format', 'stream-json', '--verbose', '--max-budget-usd', '0.40', *args]
    started = time.monotonic()
    try:
        result = pilot.command(cmd, cwd=checkout, env=env, timeout=900)
        stdout, code = result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        stdout, code = '', 124
    seconds = time.monotonic() - started
    (record / 'events.jsonl').write_text(stdout, encoding='utf-8')
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    final = next((e for e in reversed(events) if e.get('type') == 'result'), {})
    pilot.checked(['git', 'add', '-A'], cwd=checkout, env=env)
    candidate = pilot.checked(['git', 'diff', '--cached', 'HEAD'], cwd=checkout, env=env)
    source = REPOS / task['repo']
    reference = subprocess.run(['git', 'show', '--format=', task['fix']], cwd=source, capture_output=True, text=True).stdout
    scores, judge_cost = judge(task, reference, candidate, dict(env, TMPDIR=str(record)))
    # Oracle: the fix commit's own test files replace the agent's copies, then the test command decides.
    for relative in task['oracle']['files']:
        data = subprocess.run(['git', 'show', f"{task['fix']}:{relative}"], cwd=source, capture_output=True).stdout
        (checkout / relative).write_bytes(data)
    oracle = pilot.command(task['oracle']['cmd'], cwd=checkout, env=env, timeout=600)
    changed = pilot.command(['git', 'diff', '--stat', 'HEAD'], cwd=checkout, env=env).stdout.strip().splitlines()
    analysis = routing.analyse(events, '')
    row = {'task': task['id'], 'arm': arm, 'n': n, 'exit': code, 'seconds': round(seconds, 1),
           'cost_usd': final.get('total_cost_usd'), 'denials': len(final.get('permission_denials', [])),
           'oracle_pass': oracle.returncode == 0, 'files_changed': max(len(changed) - 1, 0),
           'skill_called': analysis['skill_called'], 'gate_full_before_edit': analysis['gate_full_before_edit'],
           'edited': analysis['edited'], 'judge_cost_usd': judge_cost,
           **{f'judge_{k}': scores.get(k) for k in ('behavior', 'contract', 'tests', 'minimal', 'overall')}}
    print(name, {k: row[k] for k in ('exit', 'oracle_pass', 'judge_overall', 'cost_usd')}, flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--tasks', type=Path, nargs='+', required=True)
    parser.add_argument('--arms', default='BASE')
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--only', default='', help='comma-separated task ids')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Output directory must not exist')
    if pilot.checked(['git', 'status', '--porcelain'], cwd=ROOT).strip():
        raise SystemExit('Working tree must be clean')
    tasks = [t for f in args.tasks for t in json.loads(f.read_text(encoding='utf-8'))]
    if args.only:
        tasks = [t for t in tasks if t['id'] in args.only.split(',')]
    output.mkdir(parents=True)
    shared_target = output / 'cargo-target'
    jobs = [(t, a, n) for t in tasks for a in args.arms.split(',') for n in range(1, args.n + 1)]
    random.Random(20261030).shuffle(jobs)
    plugin, core = ROOT / 'plugins' / 'kaboost', ROOT / 'core' / 'engineering-rules.md'
    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(lambda j: run(output, shared_target, *j, plugin, core), jobs))
    with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r['task'], r['arm'], r['n'])))
    print('done; total cost', round(sum(r['cost_usd'] or 0 for r in rows), 2))


if __name__ == '__main__':
    main()

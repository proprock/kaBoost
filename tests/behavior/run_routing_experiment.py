"""Compare routing variants V0-V3 on natural (uninstrumented) prompts.

Usage: python3 tests/behavior/run_routing_experiment.py OUTPUT_DIR [--large N] [--small N] [--workers N]
Requires an authenticated Claude profile; each session is capped at USD 0.40.
Raw events stay in OUTPUT_DIR; summary.csv is the sanitized record to commit.

Primary metric: the agent stated acceptance criteria, non-goals and an
alternative, or invoked a planning skill, before its first Edit/Write.
Variants V1-V3 were defined against the toolkit before ADR 006 (commit 981b982); on later
commits V0 is the adopted V2 and V1-V3 overlays no longer apply cleanly.
Variants change only model-facing text; plugin checksums in the diagnostic
copies are intentionally stale.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_pilot as pilot  # noqa: E402  (reuse frozen commit, model and prompts)

LARGE = pilot.PROMPTS['large'].split(' Before any source or test edit,')[0] + ' Implement and run focused checks.'
PROMPTS = {'small': pilot.PROMPTS['small'], 'large': LARGE}
EVALUATORS = {'small': 'acceptance_readme.py', 'large': 'acceptance_json_cli.py'}
VARIANTS = ('V0', 'V1', 'V2', 'V3')

V1_DESCRIPTION = (
    'Use BEFORE editing code when a task adds or changes a CLI flag, output format, public API, schema, config, '
    'security behavior, or anything callers or users may depend on, or when scope is unclear: discover existing '
    'contracts first, then state criteria, non-goals and alternatives. Also use to inspect or refresh repository '
    'context when onboarding, resuming stale work, or preparing a handoff.')

V2_PLAN_SKILL = '''---
name: plan-before-edit
description: Use BEFORE the first edit when a task adds or changes a CLI flag, output format, public API, schema, config, security behavior, or anything callers or users may depend on, or when scope is unclear. Finds existing contracts and states criteria, non-goals and alternatives before code changes.
---
# Plan before edit

1. Find what already depends on the thing you will change: callers, tests, docs, and current behavior for default and invalid inputs. Run or read the existing code to confirm.
2. Before the first edit, state briefly: acceptance criteria, non-goals, existing behavior that must stay unchanged, one alternative design and why it was rejected, and the checks you will run (success, failure, compatibility).
3. Then implement in small verified steps and run the checks. Escalate if new evidence raises the risk.

Skip only for typo, documentation, or one-line local fixes.
'''

V3_CORE_LINE = (
    '- Before the first edit that changes behavior, a CLI or API surface, an output format, or an interface that other code or users depend on: '
    'find what depends on it (callers, tests, docs, current behavior for default and invalid inputs), then state in a short block the acceptance criteria, '
    'non-goals, existing behavior that must stay unchanged, one rejected alternative, and the checks you will run. Skip for typo, documentation, or one-line local fixes.')

ORIGINAL_DESCRIPTION = ('Inspect or refresh repository context when onboarding, resuming stale work, or preparing a session handoff. '
                        'Use for context discovery and maintenance, not routine edits in a known repository.')


def build_variant(variant, plugin, core):
    """Rewrite copies of the plugin and core file for one variant."""
    skill = plugin / 'skills' / 'project-context' / 'SKILL.md'
    text = skill.read_text(encoding='utf-8')
    lines = text.split('\n')
    current = next(i for i, l in enumerate(lines) if l.startswith('description:'))
    core_lines = core.read_text(encoding='utf-8').split('\n')
    rule = next(i for i, l in enumerate(core_lines) if l.startswith('- For substantial uncertainty'))
    if variant == 'V1':
        lines[current] = 'description: ' + V1_DESCRIPTION
    elif variant == 'V2':
        lines[current] = 'description: ' + ORIGINAL_DESCRIPTION
        plan = plugin / 'skills' / 'plan-before-edit'
        plan.mkdir()
        (plan / 'SKILL.md').write_text(V2_PLAN_SKILL, encoding='utf-8')
        core_lines[rule] = ('- For changes to behavior, CLI or API surfaces, or anything others depend on, invoke plan-before-edit '
                            'before the first edit.')
    elif variant == 'V3':
        core_lines[rule] = V3_CORE_LINE
    skill.write_text('\n'.join(lines), encoding='utf-8')
    core.write_text('\n'.join(core_lines), encoding='utf-8')


def analyse(events):
    """Return routing metrics from stream-json events."""
    order, text_before, skills, edited = [], [], [], False
    for event in events:
        if event.get('type') != 'assistant':
            continue
        for block in event.get('message', {}).get('content', []):
            if block.get('type') == 'text' and not edited:
                text_before.append(block['text'])
            elif block.get('type') == 'tool_use':
                name = block['name']
                order.append(name)
                if name == 'Skill':
                    skills.append(block.get('input', {}).get('skill', ''))
                if name in ('Edit', 'Write') and not edited:
                    edited = True
    said = ' '.join(text_before).lower()
    stated = 'acceptance criteria' in said and 'non-goal' in said and 'alternativ' in said
    first_edit = next((i for i, n in enumerate(order) if n in ('Edit', 'Write')), None)
    skill_before = any(n == 'Skill' for n in (order[:first_edit] if first_edit is not None else order))
    return {'edited': first_edit is not None, 'skill_called': bool(skills), 'skills': ';'.join(skills),
            'skill_before_edit': skill_before, 'gate_stated_before_edit': stated,
            'gate_met': stated or skill_before, 'tools': ';'.join(order[:12])}


def run(output, variant, scenario, n, toolkit_plugin, core_src):
    name = f'{variant}-{scenario}-{n}'
    record = output / name
    record.mkdir()
    checkout = record / 'checkout'
    env = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null')
    pilot.checked(['git', 'clone', '--quiet', '--no-hardlinks', '--local', str(ROOT), str(checkout)], env=env)
    pilot.checked(['git', 'checkout', '--quiet', '--detach', pilot.COMMIT], cwd=checkout, env=env)
    plugin = record / 'plugin'
    shutil.copytree(toolkit_plugin, plugin)
    rules = checkout / '.claude' / 'engineering-rules.md'
    rules.parent.mkdir()
    shutil.copyfile(core_src, rules)
    (checkout / 'CLAUDE.md').write_text('@.claude/engineering-rules.md\n', encoding='utf-8')
    with (checkout / '.git' / 'info' / 'exclude').open('a', encoding='utf-8') as f:
        f.write('\n/CLAUDE.md\n/.claude/\n')
    build_variant(variant, plugin, rules)
    allowed = 'Read,Edit,Write,Glob,Grep,Skill,Bash(python3 *),Bash(python *),Bash(git *),Bash(tail *),Bash(echo *),Bash(cd *),Bash(ls *),Bash(cat *),Bash(wc *),Bash(grep *),Bash(head *),Bash(sed *)'
    cmd = ['claude', '-p', PROMPTS[scenario], '--model', pilot.MODEL, '--effort', 'medium',
           '--setting-sources', 'project,local', '--strict-mcp-config', '--no-session-persistence',
           '--permission-mode', 'dontAsk', '--tools', 'Read,Edit,Write,Glob,Grep,Bash,Skill',
           '--allowedTools', allowed, '--output-format', 'stream-json', '--verbose',
           '--max-budget-usd', '0.40', '--plugin-dir', str(plugin)]
    started = time.monotonic()
    try:
        result = pilot.command(cmd, cwd=checkout, env=env, timeout=900)
        stdout, code = result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        stdout, code = '', 124
    duration = time.monotonic() - started
    (record / 'events.jsonl').write_text(stdout, encoding='utf-8')
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    final = next((e for e in reversed(events) if e.get('type') == 'result'), {})
    init = next((e for e in events if e.get('subtype') == 'init'), {})
    acceptance = pilot.command([sys.executable, str(ROOT / 'tests/behavior' / EVALUATORS[scenario]), str(checkout)], cwd=checkout, env=env)
    row = {'variant': variant, 'scenario': scenario, 'n': n, 'exit': code, 'model': init.get('model'),
           'plugin_loaded': any(p.get('name') == 'ai-dev-toolkit' for p in init.get('plugins', [])),
           'seconds': round(duration, 1), 'cost_usd': final.get('total_cost_usd'),
           'denials': len(final.get('permission_denials', [])), 'acceptance_exit': acceptance.returncode,
           **analyse(events)}
    print(name, {k: row[k] for k in ('exit', 'gate_met', 'skill_called', 'acceptance_exit', 'cost_usd')}, flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--large', type=int, default=10)
    parser.add_argument('--small', type=int, default=5)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--variants', default=','.join(VARIANTS))
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Output directory must not exist')
    if pilot.checked(['git', 'status', '--porcelain'], cwd=ROOT).strip():
        raise SystemExit('Working tree must be clean')
    output.mkdir(parents=True)
    plugin, core = ROOT / 'plugins' / 'ai-dev-toolkit', ROOT / 'core' / 'engineering-rules.md'
    jobs = [(v, s, n) for v in args.variants.split(',') for s, count in (('large', args.large), ('small', args.small))
            for n in range(1, count + 1)]
    random.Random(20261029).shuffle(jobs)
    rows = []
    with ThreadPoolExecutor(args.workers) as pool:
        for row in pool.map(lambda j: run(output, *j, plugin, core), jobs):
            rows.append(row)
    with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r['scenario'], r['variant'], r['n'])))
    print('done; total cost', round(sum(r['cost_usd'] or 0 for r in rows), 2))


if __name__ == '__main__':
    main()

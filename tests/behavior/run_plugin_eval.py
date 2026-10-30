"""Run claude plugin eval on evals/ through a temporary plugin root.

Usage: python3 tests/behavior/run_plugin_eval.py OUTPUT_DIR [--estimate-only] [--max-cost-usd N] [--runs N] [-- extra eval args]
The eval directory must live inside a plugin root, but plugins/ai-dev-toolkit is generated,
so the cases stay in evals/ and are copied next to a copy of the plugin. Fixture placeholders
are filled in the copy only. Runs spend real money: without --max-cost-usd only the estimate is printed.
The cost ceiling is checked before each run starts, so concurrency is fixed at 1.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_pilot as pilot  # noqa: E402

PER_RUN_USD = 0.45  # upper bound seen for edit-capable runs: 0.42
EVAL_CLAUDE_VERSION = '2.1.308'


def cases(evals):
    return sorted(p.parent for p in evals.glob('*/prompt.md'))


def run_count(case, override):
    if override:
        return override
    match = re.search(r'^runs:\s*(\d+)', (case / 'prompt.md').read_text(encoding='utf-8'), re.M)
    return int(match.group(1)) if match else 3


def estimate(evals, runs=None):
    """Upper bound in USD: cases x runs x two arms x PER_RUN_USD."""
    return round(sum(run_count(c, runs) * 2 * PER_RUN_USD for c in cases(evals)), 2)


def assemble(destination, source=ROOT, commit=pilot.COMMIT):
    """Copy the plugin and evals into destination and fill fixture placeholders."""
    plugin = destination / 'plugin'
    shutil.copytree(source / 'plugins' / 'ai-dev-toolkit', plugin)
    evals = plugin / 'evals'
    shutil.copytree(source / 'evals', evals)
    for fixture in evals.glob('*/fixture.sh'):
        text = fixture.read_text(encoding='utf-8')
        fixture.write_text(text.replace('@SOURCE@', str(source)).replace('@COMMIT@', commit), encoding='utf-8')
    return plugin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-cost-usd', type=float)
    parser.add_argument('--runs', type=int)
    parser.add_argument('--estimate-only', action='store_true')
    parser.add_argument('extra', nargs='*')
    args = parser.parse_args()
    output = pilot.new_output_dir(args.output)
    bound = estimate(ROOT / 'evals', args.runs)
    print(f'Upper-bound cost estimate: USD {bound}')
    if args.estimate_only or args.max_cost_usd is None:
        raise SystemExit('Pass --max-cost-usd after approving the estimate to run')
    if args.max_cost_usd < PER_RUN_USD:
        raise SystemExit('Ceiling below one run')
    if pilot.checked(['git', 'status', '--porcelain'], cwd=ROOT).strip():
        raise SystemExit('Working tree must be clean')
    version = pilot.checked(['claude', '--version']).strip()
    if not version.startswith(EVAL_CLAUDE_VERSION):
        print(f'Warning: validated with Claude {EVAL_CLAUDE_VERSION}, found {version}', file=sys.stderr)
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='kaboost-eval-') as temp:
        plugin = assemble(Path(temp).resolve())
        cmd = ['claude', 'plugin', 'eval', str(plugin), '--scaffold', '--no-publish', '--trust-plugin',
               '--allow-tools', 'Edit', 'Write', '--threshold', '0.5', '-j', '1',
               '--max-cost-usd', str(args.max_cost_usd), '--output-dir', str(output),
               '--report', str(output / 'report.html'), *(['--runs', str(args.runs)] if args.runs else []), *args.extra]
        sys.exit(subprocess.run(cmd).returncode)


if __name__ == '__main__':
    main()

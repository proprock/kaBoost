"""Measure the context the toolkit adds to a session and compare it with budgets (KB-213).

Three tiers, by when the text enters the model's context:
  always     core rules (imported into the project instruction) plus the name and description of every
             skill and command (the listing the client shows on every turn);
  on demand  skill bodies and command bodies, loaded when invoked;
  init       text read only by /kaboost:init commands.
Tokens are estimated as ceil(characters / 4); the figure is a trend indicator, not a billing number.

Usage: python scripts/measure_context.py [--json] [--check]
--check exits 1 when a tier exceeds its budget, so a growing addition must be justified or simplified.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path
from build import ROOT, source_file

# Budgets in estimated tokens. Proposed with about 15% headroom over the 2026-10-30 measurement
# (see docs/context-overhead.md); raising one needs maintainer confirmation.
BUDGETS = {'always': 1500, 'skill_body_max': 600, 'command_body_max': 600}


def tokens(text):
    return math.ceil(len(text) / 4)


def front_matter(text):
    match = re.fullmatch(r'---\n(.*?)\n---\n(.*)', text, re.S)
    if not match:
        raise ValueError('Missing front matter')
    fields = dict(line.split(': ', 1) for line in match[1].splitlines())
    return fields, match[2]


def read(root, path):
    return source_file(root, path).decode('utf-8')


def measure(root=ROOT):
    manifest = json.loads(read(root, 'toolkit.json'))
    core = tokens(read(root, manifest['core']))
    skills, commands = {}, {}
    for name in manifest['skills']:
        fields, body = front_matter(read(root, f'skills/{name}/SKILL.md'))
        skills[name] = {'listing': tokens(f"{name}: {fields['description']}"), 'body': tokens(body)}
    for name in manifest.get('commands', []):
        fields, body = front_matter(read(root, f'commands/{name}.md'))
        commands[name] = {'listing': tokens(f"/{name}: {fields['description']}"), 'body': tokens(body)}
    listing = sum(item['listing'] for item in (*skills.values(), *commands.values()))
    return {
        'core': core,
        'listing': listing,
        'always': core + listing,
        'skills': skills,
        'commands': commands,
        'skill_body_max': max((s['body'] for s in skills.values()), default=0),
        'command_body_max': max((c['body'] for c in commands.values()), default=0),
    }


def violations(result):
    return [f'{key} is {result[key]} tokens, budget {limit}'
            for key, limit in BUDGETS.items() if result[key] > limit]


def render(result):
    lines = [f"always loaded: {result['always']} tokens (core {result['core']}, listing {result['listing']})"]
    for kind in ('skills', 'commands'):
        for name, item in result[kind].items():
            lines.append(f"{kind[:-1]} {name}: listing {item['listing']}, body {item['body']}")
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    result = measure()
    print(json.dumps(result, indent=2) if args.json else render(result))
    problems = violations(result)
    for problem in problems:
        print(f'over budget: {problem}', file=sys.stderr)
    return 1 if args.check and problems else 0


if __name__ == '__main__':
    raise SystemExit(main())

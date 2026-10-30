"""kaBoost init engine: managed sections in repository and global instruction files.

Standard library only. Runs only when a user invokes /kaboost:init or /kaboost:init-global; nothing here
runs at installation or in the background. File changes are marked blocks that this tool can update or remove
without touching anything outside it:

    <!-- kaboost:begin KEY vN sha=<12 hex> pre=<n> created=<0|1> -->   (or "# ..." in non-Markdown files)
    ...body...
    <!-- kaboost:end KEY -->

A feature may also install a git hook (`kind: git-hook`): the engine runs the named tool's `install` or
`uninstall` after the files are written, installing the tool with `uv tool install` first when it is missing, and
restores the files if a command fails. All of it happens only with --yes.

`sha` is the hash of the body at write time, so edits made inside a block are detected as drift and never
overwritten without --force. `pre` and `created` let disabling restore the original bytes exactly.
"""
import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
BEGIN = re.compile(r'^(?:<!-- |# )kaboost:begin (?P<key>\S+) v(?P<ver>\d+) sha=(?P<sha>[0-9a-f]{12}) '
                   r'pre=(?P<pre>\d+) created=(?P<created>[01])(?: -->)?$', re.M)
END = r'^(?:<!-- |# )kaboost:end {key}(?: -->)?$'


class Refusal(Exception):
    """A block cannot be changed safely; the reason is shown to the user."""


def load_catalog():
    return json.loads((HERE / 'catalog.json').read_text(encoding='utf-8'))


def body_of(edit):
    source = edit['body']
    if source == '{core}':
        text = (PLUGIN / 'core' / 'engineering-rules.md').read_text(encoding='utf-8')
    else:
        text = (HERE / 'features' / source).read_text(encoding='utf-8')
    return text.replace('\r\n', '\n').rstrip('\n') + '\n'


def split_front(body):
    """Split leading YAML frontmatter from the body; ('', body) when there is none."""
    if body.startswith('---\n'):
        end = body.find('\n---\n', 3)
        if end != -1:
            return body[:end + 5], body[end + 5:]
    return '', body


def is_front(text):
    return text.startswith('---\n') and text.endswith('\n---\n') and split_front(text)[0] == text


def parts(edit):
    """(frontmatter, managed body). Frontmatter stays above the begin marker so skill files keep a valid header;
    it belongs to the block's version, so changing it needs a version bump."""
    body = body_of(edit)
    return split_front(body) if edit.get('frontmatter') else ('', body)


def digest(body):
    return hashlib.sha256(body.encode('utf-8')).hexdigest()[:12]


def style_of(path):
    return 'html' if Path(path).suffix.lower() in ('.md', '.markdown') else 'hash'


def marker(style, text):
    return f'<!-- {text} -->' if style == 'html' else f'# {text}'


def render(key, version, body, style, pre, created):
    begin = marker(style, f'kaboost:begin {key} v{version} sha={digest(body)} pre={pre} created={created}')
    return f'{begin}\n{body}{marker(style, f"kaboost:end {key}")}\n'


def read(path):
    """Return (text with LF newlines, newline style, bom, existed)."""
    if not path.exists():
        return '', '\n', False, False
    raw = path.read_bytes()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig')
    crlf = '\r\n' in text and '\n' not in text.replace('\r\n', '')
    return text.replace('\r\n', '\n'), '\r\n' if crlf else '\n', bom, True


def to_bytes(text, newline, bom):
    data = text.replace('\n', newline).encode('utf-8')
    return (b'\xef\xbb\xbf' + data) if bom else data


def find_block(text, key):
    """Return the block for key as a dict, None when absent; raise Refusal on damaged markers."""
    begins = [m for m in BEGIN.finditer(text) if m.group('key') == key]
    if not begins:
        return None
    if len(begins) > 1:
        raise Refusal(f'{key}: more than one begin marker')
    begin = begins[0]
    end = re.compile(END.format(key=re.escape(key)), re.M).search(text, begin.end())
    if end is None:
        raise Refusal(f'{key}: begin marker without end marker')
    inner = text[begin.end() + 1:end.start()]
    stop = end.end() + 1 if text[end.end():end.end() + 1] == '\n' else end.end()
    return {'start': begin.start(), 'stop': stop, 'inner': inner, 'version': int(begin.group('ver')),
            'sha': begin.group('sha'), 'pre': int(begin.group('pre')), 'created': int(begin.group('created'))}


def resolve(edit, root, home):
    return Path(edit['target'].replace('{repo}', str(root)).replace('{home}', str(home)))


def hook_file(root):
    """The pre-commit hook path git uses for this repository (worktrees and core.hooksPath included), or None."""
    try:
        done = subprocess.run(['git', '-C', str(root), 'rev-parse', '--git-path', 'hooks/pre-commit'],
                              capture_output=True, text=True)
    except OSError:
        return None
    if done.returncode != 0 or not done.stdout.strip():
        return None
    path = Path(done.stdout.strip())
    return path if path.is_absolute() else root / path


def hook_state(edit, root):
    path = hook_file(root)
    if path is None:
        return 'conflict', 'not a git repository, so no git hook can be installed'
    if not path.exists():
        return 'absent', ''
    if edit['command'] in path.read_text(encoding='utf-8', errors='replace'):
        return 'enabled', ''
    return 'conflict', f'{path} exists and was not installed by {edit["command"]}'


def find_tool(name):
    """Locate a command on PATH, falling back to the folder where `uv tool install` puts executables."""
    found = shutil.which(name)
    if found or not shutil.which('uv'):
        return found
    done = subprocess.run(['uv', 'tool', 'dir', '--bin'], capture_output=True, text=True)
    return shutil.which(name, path=done.stdout.strip()) if done.returncode == 0 and done.stdout.strip() else None


def plan_hook(edit, root, install):
    """Return the commands that install or remove a git hook, or raise Refusal; nothing runs here."""
    command = edit['command']
    state, note = hook_state(edit, root)
    if state == 'conflict':
        raise Refusal(note)
    if install:
        if state == 'enabled':
            return []
        steps = []
        if find_tool(command) is None:
            if not shutil.which('uv'):
                raise Refusal(f'{command} is not installed and uv is not available to install it; install {command} first')
            steps.append(['uv', 'tool', 'install', command])
        return steps + [[command, 'install']]
    if state == 'absent':
        return []
    if find_tool(command) is None:
        raise Refusal(f'{command} was not found; delete {hook_file(root)} by hand to remove the hook')
    return [[command, 'uninstall']]


def execute(actions, root):
    results = []
    for action in actions:
        argv = list(action['argv'])
        resolved = find_tool(argv[0]) if argv[0] != 'uv' else shutil.which('uv')
        argv[0] = resolved or argv[0]
        try:
            done = subprocess.run(argv, cwd=root, capture_output=True, text=True)
            result = {'command': ' '.join(action['argv']), 'returncode': done.returncode,
                      'output': (done.stdout + done.stderr).strip()[-500:]}
        except OSError as error:
            result = {'command': ' '.join(action['argv']), 'returncode': 127, 'output': str(error)}
        results.append(result)
        if result['returncode'] != 0:
            break
    return results


def edit_state(edit, key, root, home):
    if edit.get('kind') == 'git-hook':
        return hook_state(edit, root)
    path = resolve(edit, root, home)
    text, _, _, existed = read(path)
    try:
        block = find_block(text, key)
    except Refusal as error:
        return 'conflict', str(error)
    if block is None:
        if edit['mode'] == 'own' and existed and text != '':
            return 'conflict', f'{path.name} exists and is not managed by kaBoost'
        return 'absent', ''
    body = parts(edit)[1]
    if digest(block['inner']) != block['sha']:
        return 'drift', f'{key}: the block was edited after it was written'
    if block['version'] != edit['version'] or block['sha'] != digest(body):
        return 'outdated', ''
    return 'enabled', ''


def relevant(feature, root):
    when = feature.get('when') or {}
    patterns = when.get('any_glob')
    if patterns:
        return any(next(root.glob(p), None) is not None for p in patterns)
    return True


def active_edits(feature, root, home, tools):
    """Edits that apply now. An edit without `tool` is shared (AGENTS.md, TODO.md, ...) and always applies; an edit
    for one tool applies when that tool is requested. Without targets, global scope uses the tools whose directory
    exists in the home folder and repository scope uses every tool."""
    chosen = []
    for edit in feature['edits']:
        tool = edit.get('tool')
        if tool and tools is not None and tool not in tools:
            continue
        if tool and tools is None and feature['scope'] == 'global' and not (home / f'.{tool}').is_dir():
            continue
        chosen.append(edit)
    return chosen


def feature_state(feature, root, home, tools=None):
    states = []
    for edit in active_edits(feature, root, home, tools):
        key = f"{feature['id']}:{edit['name']}"
        state, note = edit_state(edit, key, root, home)
        target = f"git hook ({edit['command']})" if edit.get('kind') == 'git-hook' else str(resolve(edit, root, home))
        states.append({'edit': edit['name'], 'target': target, 'state': state, 'note': note})
    kinds = {s['state'] for s in states}
    if not states:
        overall = 'unavailable'
    elif 'conflict' in kinds:
        overall = 'conflict'
    elif 'drift' in kinds:
        overall = 'drift'
    elif kinds == {'enabled'}:
        overall = 'enabled'
    elif kinds == {'absent'}:
        overall = 'disabled'
    elif 'outdated' in kinds and kinds <= {'enabled', 'outdated'}:
        overall = 'outdated'
    else:
        overall = 'partial'
    return overall, states


def status(catalog, scope, root, home, show_all, tools=None):
    rows = []
    for feature in catalog['features']:
        if feature['scope'] != scope:
            continue
        is_relevant = relevant(feature, root)
        if not is_relevant and not show_all:
            continue
        overall, edits = feature_state(feature, root, home, tools)
        if tools is not None and overall == 'unavailable':
            continue
        rows.append({'id': feature['id'], 'number': feature.get('number'), 'group': feature['group'],
                     'title': feature['title'], 'summary': feature['summary'], 'relevant': is_relevant,
                     'state': overall, 'edits': edits})
    return rows


def plan_apply(feature, root, home, tools, force, pending=None, actions=None):
    """Return {path: new_text} for one feature on top of the changes already pending, or raise Refusal; nothing is
    written here. The result includes the pending paths it builds on."""
    changes = dict(pending or {})
    for edit in active_edits(feature, root, home, tools):
        if edit.get('kind') == 'git-hook':
            actions.extend({'feature': feature['id'], 'argv': argv} for argv in plan_hook(edit, root, True))
            continue
        key = f"{feature['id']}:{edit['name']}"
        path = resolve(edit, root, home)
        text, _, _, existed = read(path)
        text = changes.get(path, text)
        block = find_block(text, key)
        front, body = parts(edit)
        style = style_of(path)
        if block is None:
            if edit['mode'] == 'own' and path not in changes and existed and text != '':
                raise Refusal(f'{path.name} exists and is not managed by kaBoost')
            pre = '' if text == '' else (('\n' if not text.endswith('\n') else '') + '\n')
            created = 0 if existed or path in changes else 1
            changes[path] = text + pre + front + render(key, edit['version'], body, style, len(pre), created)
            continue
        if digest(block['inner']) != block['sha'] and not force:
            raise Refusal(f'{key}: the block was edited after it was written; review it, then use --force to overwrite')
        if block['version'] == edit['version'] and block['sha'] == digest(body) and digest(block['inner']) == block['sha']:
            continue
        new = render(key, edit['version'], body, style, block['pre'], block['created'])
        head = text[:block['start']]
        if front and is_front(head):
            head = front
        changes[path] = head + new + text[block['stop']:]
    return changes


def plan_disable(feature, root, home, tools, pending=None, actions=None):
    changes = dict(pending or {})
    for edit in active_edits(feature, root, home, tools):
        if edit.get('kind') == 'git-hook':
            actions.extend({'feature': feature['id'], 'argv': argv} for argv in plan_hook(edit, root, False))
            continue
        key = f"{feature['id']}:{edit['name']}"
        path = resolve(edit, root, home)
        text = changes[path] if path in changes else read(path)[0]
        block = find_block(text, key)
        if block is None:
            continue
        if digest(block['inner']) != block['sha']:
            raise Refusal(f'{key}: the block was edited; review it and remove it by hand')
        start = block['start']
        before = text[:start]
        if edit.get('frontmatter') and is_front(before):
            before = ''
        if block['pre'] and before.endswith('\n' * block['pre']):
            before = before[:-block['pre']]
        result = before + text[block['stop']:]
        changes[path] = result
    return changes


def known_tools(catalog):
    return sorted({e['tool'] for f in catalog['features'] for e in f['edits'] if e.get('tool')})


def parse_targets(value, catalog):
    """A list of tools separated by commas or spaces; 'all' means every tool in the catalog; None means auto-detect."""
    names = [n for n in re.split(r'[,\s]+', value.lower()) if n]
    if not names:
        return None
    known = known_tools(catalog)
    if 'all' in names:
        return known
    unknown = [n for n in names if n not in known]
    if unknown:
        raise SystemExit(f'Unknown targets {unknown}; known: {known} or all')
    return list(dict.fromkeys(names))


def run(catalog, args, root, home):
    feature_ids = [i for i in args.ids.split(',') if i]
    by_id = {f['id']: f for f in catalog['features'] if f['scope'] == args.scope}
    unknown = [i for i in feature_ids if i not in by_id]
    if unknown:
        raise SystemExit(f'Unknown feature ids for scope {args.scope}: {unknown}')
    tools = parse_targets(args.targets, catalog)
    stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    report, pending, actions = [], {}, []
    for fid in feature_ids:
        feature = by_id[fid]
        mine = []
        try:
            planned = (plan_apply(feature, root, home, tools, args.force, pending, mine) if args.command == 'apply'
                       else plan_disable(feature, root, home, tools, pending, mine))
        except Refusal as error:
            report.append({'feature': fid, 'result': 'skipped', 'reason': str(error)})
            continue
        touched = [p for p, text in planned.items() if pending.get(p) != text]
        pending.update(planned)
        actions.extend(mine)
        report.append({'feature': fid, 'result': 'planned' if touched or mine else 'nothing to do',
                       'files': [str(p) for p in touched]})
    results, undo = [], []
    if args.yes and args.command == 'disable' and actions:
        results = execute(actions, root)
        if any(r['returncode'] != 0 for r in results):
            pending = {}
    changes = []
    for path, new_text in pending.items():
        old_text, newline, bom, existed = read(path)
        if new_text == old_text:
            continue
        diff = ''.join(difflib.unified_diff(old_text.splitlines(True), new_text.splitlines(True),
                                           f'a/{path.name}' if existed else '/dev/null', f'b/{path.name}'))
        deleting = new_text == '' and existed and _created(old_text)
        changes.append({'file': str(path), 'action': 'delete' if deleting else ('modify' if existed else 'create'),
                        'diff': diff})
        if args.yes:
            undo.append((path, path.read_bytes() if existed else None))
            if deleting:
                path.unlink()
                continue
            if existed:
                backup = path.with_name(f'{path.name}.kaboost-bak-{stamp}')
                backup.write_bytes(path.read_bytes())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(to_bytes(new_text, newline if existed else '\n', bom))
    if args.yes and args.command == 'apply' and actions:
        results = execute(actions, root)
    failed = any(r['returncode'] != 0 for r in results)
    if failed:
        for path, old in reversed(undo):
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        for item in report:
            if item['result'] == 'planned':
                item.update(result='failed', reason='a command failed; nothing was left half-done')
    return {'command': args.command, 'written': bool(args.yes) and not failed, 'report': report, 'changes': changes,
            'commands': [{'feature': a['feature'], 'command': ' '.join(a['argv'])} for a in actions],
            'command_results': results}


def _created(old_text):
    return any(m.group('created') == '1' for m in BEGIN.finditer(old_text))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('status', 'apply', 'disable'))
    parser.add_argument('--scope', choices=('repo', 'global'), default='repo')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--ids', default='', help='comma-separated feature ids (apply, disable)')
    parser.add_argument('--targets', default='', help='list of tools (comma-separated, e.g. claude,codex) or all; default: tools whose directory exists')
    parser.add_argument('--all', action='store_true', help='status: include features not relevant to this repository')
    parser.add_argument('--yes', action='store_true', help='write changes; without it the command only previews')
    parser.add_argument('--force', action='store_true', help='apply: overwrite a block that was edited by hand')
    args = parser.parse_args(argv)
    catalog = load_catalog()
    root, home = args.root.resolve(), args.home.resolve()
    if args.command == 'status':
        print(json.dumps({'scope': args.scope, 'features': status(catalog, args.scope, root, home, args.all, parse_targets(args.targets, catalog))}, indent=2))
        return 0
    if not args.ids:
        parser.error('--ids is required for apply and disable')
    result = run(catalog, args, root, home)
    print(json.dumps(result, indent=2))
    return 1 if any(r['returncode'] != 0 for r in result['command_results']) else 0


if __name__ == '__main__':
    sys.exit(main())

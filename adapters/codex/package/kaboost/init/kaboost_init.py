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

A target may also lie in the git hooks directory (`{git_hooks}/commit-msg`): such a file is written like any owned
file, keeps its `#!` line above the marker (`shebang`), gets the executable bit (`executable`), and is refused
outside a git repository.

Files without comment syntax (JSON hook settings) use `mode: exact`: the engine creates them only when absent, owns
them while they equal the current body (or a body listed in `previous`, then outdated), and deletes them on disable.

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
IMPORTS_AGENTS = re.compile(r'^[ \t]*@AGENTS\.md[ \t]*$', re.M)
DUPLICATE_CORE = ('Claude Code loads the core rules twice: CLAUDE.md imports .claude/kaboost/core-rules.md and also '
                  'AGENTS.md, which carries the core for Codex. Keep the AGENTS.md copy by running '
                  '`disable --scope repo --targets claude --ids core-rules`.')
SKIPPED_CLAUDE_CORE = ('Claude Code reads the core rules through AGENTS.md (CLAUDE.md imports it), so the Claude copy '
                       'was not added.')


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
    """(header, managed body). A header stays above the begin marker so the file keeps a valid start: YAML
    frontmatter for skill files, the `#!` line for scripts git runs. It belongs to the block's version, so changing
    it needs a version bump."""
    body = body_of(edit)
    if edit.get('frontmatter'):
        return split_front(body)
    if edit.get('shebang'):
        first, rest = body.split('\n', 1)
        return first + '\n', rest
    return '', body


def is_header(edit, text):
    """Whether text is exactly the header that an edit keeps above its begin marker."""
    if edit.get('frontmatter'):
        return is_front(text)
    return bool(edit.get('shebang')) and text.startswith('#!') and text.count('\n') == 1 and text.endswith('\n')


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


CLIENT_HOME_VARIABLES = {'claude': 'CLAUDE_CONFIG_DIR', 'codex': 'CODEX_HOME'}


def client_homes(home, explicit):
    """Each client's configuration directory: `{home}/.claude` and `{home}/.codex`, or, without an explicit --home,
    the directory the client itself reads from `CLAUDE_CONFIG_DIR` or `CODEX_HOME` when set."""
    homes = {tool: home / f'.{tool}' for tool in CLIENT_HOME_VARIABLES}
    if not explicit:
        for tool, variable in CLIENT_HOME_VARIABLES.items():
            if os.environ.get(variable):
                homes[tool] = Path(os.environ[variable]).expanduser().resolve()
    return homes


def resolve(edit, root, home):
    """The edit's file. `{git_hooks}` is the hooks directory git uses (worktrees and core.hooksPath included); outside
    a git repository it falls back to `.git/hooks`, which `no_hooks_dir` keeps from being created."""
    target = edit['target'].replace('{repo}', str(root))
    if '{git_hooks}' in target:
        hooks = hook_file(root, 'hooks')
        target = target.replace('{git_hooks}', str(hooks or root / '.git' / 'hooks'))
    for tool, path in home.items():
        target = target.replace(f'{{{tool}_home}}', str(path))
    return Path(target)


def no_hooks_dir(edit, root):
    """Why an edit inside the git hooks directory cannot be written here, or ''."""
    if '{git_hooks}' not in edit.get('target', ''):
        return ''
    hooks, common = hook_file(root, 'hooks'), hook_file(root, None)
    if hooks is None or common is None:
        return 'not a git repository, so no git hook can be installed'
    hooks = hooks.resolve()
    if not (hooks.is_relative_to(root) or hooks.is_relative_to(common.resolve())):
        # A shared core.hooksPath would run every repository's own copy of the script on commit.
        return f'core.hooksPath points outside this repository ({hooks}); add the hook there by hand if you want it'
    return ''


def hook_file(root, name='hooks/pre-commit'):
    """The path git uses for a hook (default: pre-commit) in this repository, worktrees and core.hooksPath included;
    with name None, the git directory that worktrees share. None outside a git repository."""
    query = ['--git-common-dir'] if name is None else ['--git-path', name]
    try:
        done = subprocess.run(['git', '-C', str(root), 'rev-parse', *query], capture_output=True, text=True)
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


def hinted(edit, kind, message):
    """Append the catalog's advice for this kind of problem (`hints.conflict`, `hints.drift`), if it has one."""
    hint = (edit.get('hints') or {}).get(kind)
    return f'{message}. {hint}' if hint else message


def continuation_lines(text):
    """Line numbers that continue an entry (`- [ ] ...` or `- [x] ...`) instead of starting a new one; a blank line,
    a heading or a marker ends an entry."""
    bad, in_entry = [], False
    for number, line in enumerate(text.split('\n'), 1):
        if line.startswith('- ['):
            in_entry = True
        elif not line.strip() or line.startswith(('#', '<!--')):
            in_entry = False
        elif in_entry:
            bad.append(number)
    return bad


def line_warnings(catalog, root, home, scope):
    """Files managed by an edit with `one_line_entries` whose entries span several lines, one warning per file."""
    warnings = []
    for feature in catalog['features']:
        if feature['scope'] != scope:
            continue
        for edit in feature['edits']:
            if not edit.get('one_line_entries'):
                continue
            path = resolve(edit, root, home)
            text = read(path)[0]
            try:
                block = find_block(text, f"{feature['id']}:{edit['name']}")
            except Refusal:
                continue
            if block is None:
                continue
            bad = continuation_lines(text)
            if bad:
                warnings.append(f'{path.name}: {len(bad)} line(s) are not one-line entries (first at line {bad[0]}). '
                                'Edit the file so each entry is one line that starts with "- [ ] <id>:" (or "- [x]" in '
                                'DONE.md); the line has no length limit, so join the context and the approach onto it')
    return warnings


def exact_state(edit, path, text=None):
    """A file without comment syntax (JSON) that kaBoost owns only while it equals a body it wrote: the current one
    (enabled) or one listed in `previous` (outdated). A file naming the `owner` script otherwise is drift; any other
    existing file is the user's (conflict)."""
    if text is None:
        text, _, _, existed = read(path)
        if not existed:
            return 'absent', ''
    current = digest(text)
    if current == digest(body_of(edit)):
        return 'enabled', ''
    if current in edit.get('previous', []):
        return 'outdated', ''
    if edit['owner'] in text:
        return 'drift', hinted(edit, 'drift', f'{path.name} was edited after it was written')
    return 'conflict', hinted(edit, 'conflict', f'{path.name} exists and is not managed by kaBoost')


def edit_state(edit, key, root, home):
    if edit.get('kind') == 'git-hook':
        return hook_state(edit, root)
    if no_hooks_dir(edit, root):
        return 'conflict', no_hooks_dir(edit, root)
    path = resolve(edit, root, home)
    if edit['mode'] == 'exact':
        return exact_state(edit, path)
    text, _, _, existed = read(path)
    try:
        block = find_block(text, key)
    except Refusal as error:
        return 'conflict', str(error)
    if block is None:
        if edit['mode'] == 'own' and existed and text != '':
            return 'conflict', hinted(edit, 'conflict', f'{path.name} exists and is not managed by kaBoost')
        return 'absent', ''
    body = parts(edit)[1]
    if digest(block['inner']) != block['sha']:
        return 'drift', hinted(edit, 'drift', f'{key}: the block was edited after it was written')
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
        if tool and tools is None and feature['scope'] == 'global' and not home[tool].is_dir():
            continue
        chosen.append(edit)
    return chosen


def feature_state(feature, root, home, tools=None):
    states = []
    via_agents = feature['id'] == 'core-rules' and feature['scope'] == 'repo' and claude_reads_agents_core(root)
    for edit in active_edits(feature, root, home, tools):
        key = f"{feature['id']}:{edit['name']}"
        state, note = edit_state(edit, key, root, home)
        if via_agents and edit.get('tool') == 'claude' and state == 'absent':
            state, note = 'enabled', 'Claude Code reads the core rules through AGENTS.md, which CLAUDE.md imports'
        elif state == 'absent' and key == 'agents-import:import' and import_present(key, read(resolve(edit, root, home))[0]):
            state, note = 'enabled', PRESENT_IMPORT
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


PRESENT_IMPORT = 'CLAUDE.md already imports AGENTS.md outside kaBoost blocks; nothing to add'


def import_present(key, text):
    """The agents-import line is already in CLAUDE.md, written by the user rather than by kaBoost."""
    return key == 'agents-import:import' and find_block(text, key) is None and IMPORTS_AGENTS.search(text) is not None


def core_paths(root, pending):
    """CLAUDE.md and AGENTS.md as they will be after the pending changes."""
    return [pending[p] if p in pending else read(p)[0] for p in (root / 'CLAUDE.md', root / 'AGENTS.md')]


def claude_reads_agents_core(root, pending=None):
    claude, agents = core_paths(root, pending or {})
    try:
        return IMPORTS_AGENTS.search(claude) is not None and find_block(agents, 'core-rules:rules-codex') is not None
    except Refusal:
        return False


def claude_has_own_core(root, pending=None):
    try:
        return find_block(core_paths(root, pending or {})[0], 'core-rules:import') is not None
    except Refusal:
        return False


def core_warnings(root, pending=None):
    """Repository scope: the core reaches Claude Code twice, through its own copy and through AGENTS.md."""
    return [DUPLICATE_CORE] if claude_has_own_core(root, pending) and claude_reads_agents_core(root, pending) else []


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
        if no_hooks_dir(edit, root):
            raise Refusal(no_hooks_dir(edit, root))
        path = resolve(edit, root, home)
        if edit['mode'] == 'exact':
            state, note = exact_state(edit, path, changes.get(path))
            if state == 'conflict' or (state == 'drift' and not force):
                raise Refusal(note)
            if state != 'enabled':
                changes[path] = body_of(edit)
            continue
        text, _, _, existed = read(path)
        text = changes.get(path, text)
        block = find_block(text, key)
        front, body = parts(edit)
        style = style_of(path)
        if block is None and import_present(key, text):
            continue
        if block is None:
            if edit['mode'] == 'own' and path not in changes and existed and text != '':
                raise Refusal(hinted(edit, 'conflict', f'{path.name} exists and is not managed by kaBoost'))
            pre = '' if text == '' else (('\n' if not text.endswith('\n') else '') + '\n')
            created = 0 if existed or path in changes else 1
            changes[path] = text + pre + front + render(key, edit['version'], body, style, len(pre), created)
            continue
        if digest(block['inner']) != block['sha'] and not force:
            raise Refusal(hinted(edit, 'drift', f'{key}: the block was edited after it was written; review it, '
                                 'then use --force to overwrite'))
        if block['version'] == edit['version'] and block['sha'] == digest(body) and digest(block['inner']) == block['sha']:
            continue
        new = render(key, edit['version'], body, style, block['pre'], block['created'])
        head = text[:block['start']]
        if front and is_header(edit, head):
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
        if edit['mode'] == 'exact':
            state, _ = exact_state(edit, path, changes.get(path))
            if state == 'drift':
                raise Refusal(f'{path.name} was edited after it was written; review it and remove it by hand')
            if state in ('enabled', 'outdated'):
                changes[path] = ''
            continue
        text = changes[path] if path in changes else read(path)[0]
        block = find_block(text, key)
        if block is None:
            continue
        if digest(block['inner']) != block['sha']:
            raise Refusal(f'{key}: the block was edited; review it and remove it by hand')
        start = block['start']
        before = text[:start]
        if is_header(edit, before):
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

    def plan_all(without_claude_core):
        report, pending, actions = [], {}, []
        for fid in feature_ids:
            feature, feature_tools = by_id[fid], tools
            if without_claude_core and fid == 'core-rules':
                feature_tools = [t for t in (tools or known_tools(catalog)) if t != 'claude']
            mine = []
            try:
                planned = (plan_apply(feature, root, home, feature_tools, args.force, pending, mine)
                           if args.command == 'apply' else plan_disable(feature, root, home, feature_tools, pending, mine))
            except Refusal as error:
                report.append({'feature': fid, 'result': 'skipped', 'reason': str(error)})
                continue
            touched = [p for p, text in planned.items() if pending.get(p) != text]
            pending.update(planned)
            actions.extend(mine)
            report.append({'feature': fid, 'result': 'planned' if touched or mine else 'nothing to do',
                           'files': [str(p) for p in touched]})
        return report, pending, actions

    report, pending, actions = plan_all(False)
    repo_apply = args.command == 'apply' and args.scope == 'repo'
    if (repo_apply and 'core-rules' in feature_ids and core_warnings(root, pending)
            and not claude_has_own_core(root)):
        report, pending, actions = plan_all(True)
        for item in report:
            if item['feature'] == 'core-rules':
                item['note'] = SKIPPED_CLAUDE_CORE
    warnings = core_warnings(root, pending) if args.scope == 'repo' else []
    exact_paths = {resolve(e, root, home) for fid in feature_ids for e in by_id[fid]['edits'] if e.get('mode') == 'exact'}
    executable = {resolve(e, root, home) for fid in feature_ids for e in by_id[fid]['edits'] if e.get('executable')}
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
        deleting = new_text == '' and existed and (_created(old_text) or path in exact_paths)
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
            if path in executable:
                # git ignores a hook without the executable bit on POSIX, and the commit then goes through unchecked.
                path.chmod(path.stat().st_mode | 0o111)
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
    return {'command': args.command, 'written': bool(args.yes) and not failed, 'report': report,
            'warnings': warnings, 'changes': changes,
            'commands': [{'feature': a['feature'], 'command': ' '.join(a['argv'])} for a in actions],
            'command_results': results}


def _created(old_text):
    return any(m.group('created') == '1' for m in BEGIN.finditer(old_text))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=('status', 'apply', 'disable'))
    parser.add_argument('--scope', choices=('repo', 'global'), default='repo')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--home', type=Path, help='home folder for global scope; default: the user home, with '
                        'CLAUDE_CONFIG_DIR and CODEX_HOME honoured')
    parser.add_argument('--ids', default='', help='comma-separated feature ids (apply, disable)')
    parser.add_argument('--targets', default='', help='list of tools (comma-separated, e.g. claude,codex) or all; default: tools whose directory exists')
    parser.add_argument('--all', action='store_true', help='status: include features not relevant to this repository')
    parser.add_argument('--yes', action='store_true', help='write changes; without it the command only previews')
    parser.add_argument('--force', action='store_true', help='apply: overwrite a block that was edited by hand')
    args = parser.parse_args(argv)
    catalog = load_catalog()
    root = args.root.resolve()
    home = client_homes((args.home or Path.home()).resolve(), explicit=args.home is not None)
    if args.command == 'status':
        features = status(catalog, args.scope, root, home, args.all, parse_targets(args.targets, catalog))
        warnings = (core_warnings(root) if args.scope == 'repo' else []) + line_warnings(catalog, root, home, args.scope)
        print(json.dumps({'scope': args.scope, 'features': features, 'warnings': warnings}, indent=2))
        return 0
    if not args.ids:
        parser.error('--ids is required for apply and disable')
    result = run(catalog, args, root, home)
    print(json.dumps(result, indent=2))
    return 1 if any(r['returncode'] != 0 for r in result['command_results']) else 0


if __name__ == '__main__':
    sys.exit(main())

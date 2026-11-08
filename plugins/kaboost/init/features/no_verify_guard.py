"""Agent hook: block git commands that skip the repository's hooks.

Claude Code and Codex run this before a shell tool call and pass the call as JSON on stdin. It exits with code 2 and
a reason on stderr when the command is `git commit` with `--no-verify` or `-n`, `git push --no-verify`, or either with
`-c core.hooksPath=...`; otherwise it exits 0. Input it cannot read never blocks. Standard library only.
"""
import json
import os
import shlex
import sys

SHELLS = {'bash', 'sh', 'zsh', 'powershell', 'pwsh', 'cmd'}
SEPARATORS = {'&&', '||', ';', '|', '&', '\n', '(', ')'}
GLOBAL_WITH_VALUE = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--config-env'}
# Short commit options whose value follows (in the same cluster or as the next word).
COMMIT_VALUE_SHORT = set('mFCct')
COMMIT_OPTIONAL_SHORT = set('uS')
COMMIT_VALUE_LONG = {'--message', '--file', '--author', '--date', '--template', '--reuse-message', '--reedit-message',
                     '--fixup', '--squash', '--cleanup', '--trailer', '--pathspec-from-file'}
REASON = ('kaBoost no-verify-guard: this command skips the git hooks that check every commit. Run it without '
          '--no-verify (or -n, or core.hooksPath) and fix what the hooks report; if a hook itself is broken, tell the user '
          'instead of bypassing it.')


def segments(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    words, current = [], []
    for token in lexer:
        if token in SEPARATORS or set(token) <= set('&|;()'):
            if current:
                words.append(current)
            current = []
        else:
            current.append(token)
    if current:
        words.append(current)
    return words


def commit_skips_hooks(args):
    skip_value = False
    for arg in args:
        if skip_value:
            skip_value = False
            continue
        if arg == '--':
            return False
        if arg == '--no-verify':
            return True
        if arg.startswith('--'):
            skip_value = arg in COMMIT_VALUE_LONG
            continue
        if arg.startswith('-') and len(arg) > 1:
            for index, char in enumerate(arg[1:], 1):
                if char == 'n':
                    return True
                if char in COMMIT_OPTIONAL_SHORT:
                    break
                if char in COMMIT_VALUE_SHORT:
                    skip_value = index == len(arg) - 1
                    break
    return False


def program(word):
    name = os.path.basename(word.replace('\\', '/')).lower()
    return name[:-4] if name.endswith('.exe') else name


def git_bypass(words):
    while words and '=' in words[0] and not words[0].startswith('-'):
        words = words[1:]
    if not words:
        return False
    if program(words[0]) in SHELLS:
        # A shell running a command string (`bash -lc "..."`, `powershell.exe -Command '...'`): check that string.
        for flag, script in zip(words[1:], words[2:]):
            if flag.lower() in ('-c', '-lc', '-command', '/c'):
                return bypass(script)
        return False
    if program(words[0]) != 'git':
        return False
    rest, hooks_path = words[1:], False
    while rest and rest[0].startswith('-'):
        option = rest.pop(0)
        if option in GLOBAL_WITH_VALUE and rest:
            value = rest.pop(0)
            hooks_path = hooks_path or (option == '-c' and value.lower().startswith('core.hookspath'))
    if not rest:
        return False
    sub, args = rest[0], rest[1:]
    if sub == 'commit':
        return hooks_path or commit_skips_hooks(args)
    if sub == 'push':
        options = args[:args.index('--')] if '--' in args else args
        return hooks_path or '--no-verify' in options
    return False


def bypass(command):
    try:
        return any(git_bypass(words) for words in segments(command))
    except ValueError:
        return False


def main():
    try:
        call = json.loads(sys.stdin.read())
        command = call.get('tool_input', {}).get('command')
    except (ValueError, AttributeError):
        return 0
    if isinstance(command, str) and bypass(command):
        print(REASON, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())

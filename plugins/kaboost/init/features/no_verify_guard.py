"""Agent hook: block git commands that skip the repository's hooks.

Claude Code and Codex run this before a shell tool call and pass the call as JSON on stdin. It exits with code 2 and
a reason on stderr when the command is `git commit` with `--no-verify` (or an unambiguous abbreviation) or `-n`,
`git push --no-verify`, or a git command that overrides `core.hooksPath` (`-c`, `--config-env`, `GIT_CONFIG_*`
variables, `git config`); otherwise it exits 0. Input it cannot read never blocks. It is a guardrail against a habit,
not a sandbox: a command built at run time (eval, scripts, aliases) is not inspected. Standard library only.
"""
import json
import os
import shlex
import sys

SHELLS = {'bash', 'sh', 'zsh', 'powershell', 'pwsh', 'cmd'}
WRAPPERS = {'env', 'command', 'exec', 'nice', 'nohup', 'sudo', 'time'}
# Options of the wrappers above that take a value (`env -u NAME`, `sudo -u user`, `nice -n 10`, `env -C dir`).
WRAPPER_VALUE_OPTIONS = {'-u', '-g', '-n', '-C', '--unset', '--chdir', '--user', '--group'}
CONFIG_READS ={'--get', '--get-all', '--get-regexp', '--list', '-l', 'get', 'list'}
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
        if no_verify(arg):
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


def no_verify(arg):
    """`--no-verify` or an abbreviation git accepts for it (`--no-ver` is ambiguous with `--no-verbose`)."""
    return len(arg) >= len('--no-veri') and '--no-verify'.startswith(arg)


def hooks_path(word):
    return 'core.hookspath' in word.lower()


def shell_script(words):
    """The command string a shell runs (`bash -lc "..."`, `powershell.exe -Command '...'`), or None."""
    for flag, script in zip(words[1:], words[2:]):
        low = flag.lower()
        if low == '/c' or (low.startswith('-') and not low.startswith('--') and
                           ('c' in low[1:] if len(low) <= 4 else 'command'.startswith(low[1:]))):
            return script
    return None


def git_bypass(words):
    overrides = False
    while words:
        if '=' in words[0] and not words[0].startswith('-'):
            overrides = overrides or hooks_path(words[0])
        elif words[0] in WRAPPER_VALUE_OPTIONS:
            words = words[1:]
        elif program(words[0]) in WRAPPERS or words[0].startswith('-'):
            pass
        else:
            break
        words = words[1:]
    if not words:
        return False
    if program(words[0]) in SHELLS:
        script = shell_script(words)
        return script is not None and bypass(script)
    if program(words[0]) != 'git':
        return False
    rest = words[1:]
    while rest and rest[0].startswith('-'):
        option = rest.pop(0)
        overrides = overrides or hooks_path(option)
        if option in GLOBAL_WITH_VALUE and rest:
            overrides = overrides or hooks_path(rest.pop(0))
    if not rest:
        return False
    sub, args = rest[0], rest[1:]
    if sub == 'config':
        return any(hooks_path(a) for a in args) and not any(a in CONFIG_READS for a in args)
    if sub == 'commit':
        return overrides or commit_skips_hooks(args)
    if sub == 'push':
        options = args[:args.index('--')] if '--' in args else args
        return overrides or any(no_verify(a) for a in options)
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

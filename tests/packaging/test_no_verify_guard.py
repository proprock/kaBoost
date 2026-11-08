import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'init' / 'features'))
import no_verify_guard as guard  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_bypasses_are_found(self):
        for command in (
            'git commit --no-verify -m "x"',
            'git commit -n -m x',
            'git commit -anm "x"',
            'git -C sub commit --no-verify',
            'cd a && FOO=1 git commit -qn',
            'git add . ; git commit --no-verify',
            'git push --no-verify origin main',
            'git -c core.hooksPath=/dev/null commit -m x',
            '/usr/bin/git commit --no-verify',
            '"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command \'git commit --no-verify -m probe\'',
            'bash -lc "git commit -n -m x"',
        ):
            self.assertTrue(guard.bypass(command), command)

    def test_variants_that_also_skip_hooks_are_found(self):
        for command in (
            'git commit --no-veri -m x',
            'git push --no-verif',
            'GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git commit -m x',
            'git --config-env=core.hooksPath=EMPTY commit -m x',
            'git config core.hooksPath /dev/null',
            'env -u HOME git commit -n -m x',
            'sudo git commit --no-verify',
            'bash -ec "git commit --no-verify"',
        ):
            self.assertTrue(guard.bypass(command), command)
        for command in ('git config --get core.hooksPath', 'git commit --no-ver -m x', 'git commit --verbose'):
            self.assertFalse(guard.bypass(command), command)

    def test_ordinary_commands_pass(self):
        for command in (
            'git commit -m "skip --no-verify here"',
            'git commit -m -n',
            'git commit -am "fix -n flag"',
            'git commit --amend --no-edit',
            'git push -n origin main',
            'git log --no-verify-signatures',
            'echo git commit --no-verify',
            'git status',
            'git commit -m "unbalanced',
            '',
        ):
            self.assertFalse(guard.bypass(command), command)

    def run_hook(self, payload):
        err = io.StringIO()
        with mock.patch.object(sys, 'stdin', io.StringIO(payload)), contextlib.redirect_stderr(err):
            code = guard.main()
        return code, err.getvalue()

    def test_hook_blocks_with_exit_2_and_a_reason(self):
        code, err = self.run_hook(json.dumps({'tool_name': 'Bash', 'tool_input': {'command': 'git commit -n -m x'}}))
        self.assertEqual(code, 2)
        self.assertIn('--no-verify', err)
        self.assertIn('fix', err)

    def test_hook_never_blocks_on_input_it_does_not_understand(self):
        for payload in ('not json', '{}', json.dumps({'tool_input': {'command': ['git', 'commit', '-n']}})):
            self.assertEqual(self.run_hook(payload), (0, ''), payload)
        self.assertEqual(self.run_hook(json.dumps({'tool_input': {'command': 'git status'}})), (0, ''))


if __name__ == '__main__':
    unittest.main()

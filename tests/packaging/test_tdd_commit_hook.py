"""The tdd-commit-hook feature end to end: the engine installs a commit-msg hook and real `git commit` runs it."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'init'))
import kaboost_init as init  # noqa: E402

RED = 'test: add is exact (KB-7)\n\nExpected failing: tests.test_calc\n\nTDD: red\n'
GREEN = 'feat: exact add (KB-7)\n\nTDD: green\n'


class CommitHookTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name).resolve() / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'user.name', 'test')
        self.git('config', 'commit.gpgsign', 'false')
        (self.repo / 'README.md').write_text('demo\n')
        self.git('add', '.')
        self.git('commit', '-q', '-m', 'init')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            init.main(['apply', '--root', str(self.repo), '--ids', 'tdd-commit-hook', '--yes'])
        self.assertTrue(json.loads(out.getvalue())['written'], out.getvalue())

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, capture_output=True, text=True)

    def commit(self, message, path, *extra):
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(file.read_text() + 'x\n' if file.exists() else 'x\n')
        self.git('add', path)
        (self.repo.parent / 'msg').write_text(message)
        return self.git('commit', '-q', '-F', str(self.repo.parent / 'msg'), *extra)

    def test_valid_red_then_green_pass(self):
        self.assertEqual(self.commit(RED, 'tests/test_calc.py').returncode, 0)
        self.assertEqual(self.commit(GREEN, 'calc.py').returncode, 0)

    def test_red_without_expected_failing_is_rejected_with_the_fix(self):
        done = self.commit('test: add is exact (KB-7)\n\nTDD: red\n', 'tests/test_calc.py')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('Expected failing:', done.stderr)
        self.assertEqual(self.git('rev-list', '--count', 'HEAD').stdout.strip(), '1')

    def test_red_without_task_id_is_rejected(self):
        done = self.commit('test: add is exact\n\nExpected failing: tests.test_calc\n\nTDD: red\n', 'tests/test_calc.py')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('task ID', done.stderr)

    def test_green_without_an_earlier_red_of_its_task_is_rejected(self):
        self.assertEqual(self.commit(RED.replace('KB-7', 'KB-8'), 'tests/test_calc.py').returncode, 0)
        done = self.commit(GREEN, 'calc.py')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('KB-7', done.stderr)

    def test_commits_without_a_tdd_trailer_and_text_after_scissors_are_not_checked(self):
        self.assertEqual(self.commit('docs: notes\n', 'notes.md').returncode, 0)
        scissors = 'docs: more\n# ------------------------ >8 ------------------------\nTDD: red\n'
        self.assertEqual(self.commit(scissors, 'notes.md', '--cleanup=scissors').returncode, 0)


if __name__ == '__main__':
    unittest.main()

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import audit_tdd as audit  # noqa: E402

CHECK = f'{sys.executable} -c "import sys; sys.path.insert(0, \'.\'); import calc; sys.exit(0 if calc.add(1, 2) == 3 else 1)"'


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.git('init', '-q')
        self.git('config', 'user.email', 'a@example.com')
        self.git('config', 'user.name', 'A')

    def git(self, *args):
        subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True)

    def commit(self, files, message):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)

    def audit(self, *extra):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = audit.main([*extra, '--repo', str(self.repo)])
        return code, out.getvalue(), err.getvalue()

    def pair(self, green_files=None, red_files=None):
        self.commit({'README.md': 'x'}, 'KB-1: start')
        self.commit(red_files or {'tests/test_calc.py': 'tests'},
                    'KB-7: test: add is exact\n\nTDD: red\nExpected failing: tests/test_calc.py')
        self.commit(green_files or {'calc.py': 'def add(a, b):\n    return a + b\n'}, 'KB-7: implement add\n\nTDD: green')

    @unittest.skipIf(sys.platform == 'win32', 'the test command runs through a POSIX shell')
    def test_valid_pair_passes_structure_and_execution(self):
        self.commit({'README.md': 'x', 'calc.py': 'def add(a, b):\n    return 0\n'}, 'KB-1: start')
        self.commit({'tests/test_calc.py': 'tests'}, 'KB-7: test: add\n\nTDD: red\nExpected failing: tests/test_calc.py')
        self.commit({'calc.py': 'def add(a, b):\n    return a + b\n'}, 'KB-7: implement\n\nTDD: green')
        code, out, err = self.audit('--run', CHECK)
        self.assertEqual((code, err), (0, ''), out)
        self.assertIn('KB-7: red', out)

    @unittest.skipIf(sys.platform == 'win32', 'the test command runs through a POSIX shell')
    def test_red_that_passes_is_reported(self):
        self.commit({'calc.py': 'def add(a, b):\n    return a + b\n'}, 'KB-1: start')
        self.commit({'tests/test_calc.py': 'tests'}, 'KB-7: test\n\nTDD: red\nExpected failing: tests/test_calc.py')
        self.commit({'calc.py': '# refactor\ndef add(a, b):\n    return a + b\n'}, 'KB-7: tidy\n\nTDD: green')
        code, _, err = self.audit('--run', CHECK)
        self.assertEqual(code, 1)
        self.assertIn('pass on the red commit', err)

    def test_structural_problems(self):
        self.pair(red_files={'tests/test_calc.py': 't', 'calc.py': 'def add(a, b):\n    return 0\n'})
        code, _, err = self.audit()
        self.assertEqual(code, 1)
        self.assertIn('red commit changes non-test files', err)

    def test_unpaired_commits_are_reported(self):
        self.commit({'tests/test_a.py': 't'}, 'KB-7: test\n\nTDD: red\nExpected failing: tests/test_a.py')
        self.commit({'a.py': 'a'}, 'KB-8: other\n\nTDD: green')
        code, _, err = self.audit()
        self.assertEqual(code, 1)
        self.assertIn('has no green commit', err)
        self.assertIn('has no earlier red commit', err)

    def test_missing_expected_line_and_empty_history(self):
        self.commit({'README.md': 'x'}, 'KB-1: start')
        code, out, _ = self.audit()
        self.assertEqual(code, 0)
        self.assertIn('No TDD', out)
        self.commit({'tests/test_a.py': 't'}, 'KB-7: test\n\nTDD: red')
        self.commit({'a.py': 'a'}, 'KB-7: fix\n\nTDD: green')
        code, _, err = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("no 'Expected failing:'", err)


if __name__ == '__main__':
    unittest.main()

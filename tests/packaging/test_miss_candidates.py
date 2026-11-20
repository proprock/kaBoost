"""Miss-log candidates from git history (KB-250)."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import kaboost_miss_candidates as misses  # noqa: E402

MARKER = '<!-- kaboost:begin tdd-commits:rules v1 sha=000000000000 pre=0 created=0 -->\nrules\n'


class MissCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve() / 'demo'
        self.repo.mkdir()
        self.git('init', '-q', '-b', 'master')
        self.git('config', 'user.email', 'a@example.com')
        self.git('config', 'user.name', 'A')
        self.commit({'README.md': 'start\n'}, 'chore: start')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        done = subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True, text=True,
                              env=dict(os.environ, GIT_COMMITTER_DATE='2026-11-10T12:00:00 +0000'))
        return done.stdout.strip()

    def commit(self, files, message):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message, '--date=2026-11-10T12:00:00 +0000')
        return self.git('rev-parse', 'HEAD')

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = misses.main([*args, '--cwd', str(self.repo)])
        return code, out.getvalue()

    def kinds(self):
        return [c['kind'] for c in misses.candidates(f'{self.base}..HEAD', self.repo, 'master')]

    def test_squash_merge_in_a_tdd_commits_repository_is_a_candidate(self):
        self.commit({'AGENTS.md': MARKER}, 'docs: enable tdd-commits')
        self.commit({'src/a.py': '1', 'tests/test_a.py': '1'}, 'feat(a): add a (AH-1) (#12)')
        self.assertIn('squash', self.kinds())

    def test_squash_merge_without_the_tdd_commits_marker_is_not_a_candidate(self):
        self.commit({'AGENTS.md': '# Rules\n'}, 'docs: rules')
        self.commit({'src/a.py': '1'}, 'chore: tidy a (#12)')
        self.assertNotIn('squash', self.kinds())

    def test_feat_without_a_red_commit_is_unpaired(self):
        self.commit({'src/a.py': '1'}, 'feat(a): add a (AH-1)')
        self.assertEqual(self.kinds(), ['unpaired'])

    def test_fix_with_a_red_commit_is_not_unpaired(self):
        self.commit({'tests/test_a.py': '1'}, 'test(a): a is exact (AH-2)\n\nExpected failing: tests/test_a.py\n\nTDD: red')
        self.commit({'src/a.py': '1'}, 'fix(a): make a exact (AH-2)\n\nTDD: green')
        self.assertEqual(self.kinds(), [])

    def test_docs_only_feat_is_not_unpaired(self):
        self.commit({'docs/a.txt': '1', 'NOTES.md': '1'}, 'feat: document a (AH-3)')
        self.assertEqual(self.kinds(), [])

    def test_rework_is_a_candidate(self):
        self.commit({'tests/test_a.py': '1'}, 'test(a): a (AH-4)\n\nExpected failing: tests/test_a.py\n\nTDD: red')
        self.commit({'src/a.py': '1'}, 'feat(a): add a (AH-4)\n\nTDD: green')
        self.commit({'tests/test_a.py': '2'}, 'test(a): a again (AH-5)\n\nExpected failing: tests/test_a.py\n\nTDD: red')
        self.commit({'src/a.py': '2'}, 'fix(a): correct a (AH-5)\n\nTDD: green')
        self.assertEqual(self.kinds(), ['rework'])

    def test_rows_follow_the_miss_log_columns(self):
        self.commit({'src/a.py': '1'}, 'feat(a): add a (AH-1)')
        code, out = self.run_main(f'{self.base}..HEAD')
        self.assertEqual(code, 0)
        row = next(line for line in out.splitlines() if line.startswith('| 2026-11-10'))
        cells = [c.strip() for c in row.strip('|').split('|')]
        self.assertEqual(len(cells), 6, row)
        self.assertEqual((cells[1], cells[2], cells[4]), ('demo', 'AH-1', 'git history'))
        self.assertIn('unpaired: 1', out)

    def test_empty_range_prints_no_candidates(self):
        code, out = self.run_main('HEAD..HEAD')
        self.assertEqual(code, 0)
        self.assertIn('no candidates', out)

    def test_outside_a_git_repository_fails_with_a_message(self):
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(SystemExit) as raised:
                misses.main(['HEAD~1..HEAD', '--cwd', other])
        self.assertIn('git', str(raised.exception.code))


if __name__ == '__main__':
    unittest.main()

"""M2 rework rate as defined in docs/real-use-evidence.md (KB-025)."""
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
import kaboost_rework_rate as rework  # noqa: E402

DAY = 86400
START = 1767225600  # 2026-01-01T00:00:00Z


class ReworkRateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.git('init', '-q', '-b', 'master')
        self.git('config', 'user.email', 'a@example.com')
        self.git('config', 'user.name', 'A')
        self.commit({'README.md': 'start\n'}, 'chore: start', day=0)

    def git(self, *args, date=None):
        env = dict(os.environ)
        if date is not None:
            env['GIT_COMMITTER_DATE'] = f'{date} +0000'
        done = subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True, text=True, env=env)
        return done.stdout.strip()

    def commit(self, files, message, day):
        for name, text in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        stamp = START + day * DAY
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message, f'--date={stamp} +0000', date=stamp)
        return self.git('rev-parse', 'HEAD')

    def subjects(self, rows):
        return [row['subject'] for row in rows]

    def test_fix_within_seven_days_is_rework(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/a.py': '2'}, 'fix: correct a', day=7)
        result = rework.measure('HEAD~2..HEAD', self.repo)
        self.assertEqual(self.subjects(result['code']), ['feat: add a', 'fix: correct a'])
        self.assertEqual(self.subjects(result['rework']), ['fix: correct a'])

    def test_fix_after_eight_days_is_not_rework(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/a.py': '2'}, 'fix: correct a', day=9)
        self.assertEqual(rework.measure('HEAD~2..HEAD', self.repo)['rework'], [])

    def test_revert_and_scoped_fix_count(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/a.py': '2'}, 'fix(a)!: correct a (AH-7)', day=2)
        self.commit({'src/a.py': '1'}, 'Revert "fix(a)!: correct a (AH-7)"', day=3)
        result = rework.measure('HEAD~3..HEAD', self.repo)
        self.assertEqual(len(result['rework']), 2)

    def test_fix_of_a_different_file_is_not_rework(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/b.py': '1'}, 'fix: correct b', day=2)
        self.assertEqual(rework.measure('HEAD~2..HEAD', self.repo)['rework'], [])

    def test_docs_only_fix_is_not_a_code_commit(self):
        self.commit({'docs/guide.txt': '1', 'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'docs/guide.txt': '2', 'NOTES.md': 'x', '.github/ci.yml': 'x'}, 'fix: docs', day=2)
        result = rework.measure('HEAD~2..HEAD', self.repo)
        self.assertEqual(self.subjects(result['code']), ['feat: add a'])
        self.assertEqual(result['rework'], [])

    def test_merge_commit_is_ignored(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        base = self.git('rev-parse', 'HEAD~1')
        self.git('checkout', '-q', '-b', 'topic')
        self.commit({'src/b.py': '1'}, 'feat: add b', day=2)
        self.git('checkout', '-q', 'master')
        stamp = START + 3 * DAY
        self.git('merge', '-q', '--no-ff', '-m', 'fix: merge topic touching a', 'topic', date=stamp)
        result = rework.measure(f'{base}..master', self.repo)
        self.assertEqual(sorted(self.subjects(result['code'])), ['feat: add a', 'feat: add b'])
        self.assertEqual(result['rework'], [])

    def test_earlier_commit_outside_the_range_still_counts(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/a.py': '2'}, 'fix: correct a', day=3)
        result = rework.measure('HEAD~1..HEAD', self.repo)
        self.assertEqual(self.subjects(result['rework']), ['fix: correct a'])

    def test_report_prints_counts_and_rate(self):
        self.commit({'src/a.py': '1'}, 'feat: add a', day=1)
        self.commit({'src/a.py': '2'}, 'fix: correct a', day=2)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(rework.main(['HEAD~2..HEAD', '--cwd', str(self.repo)]), 0)
        self.assertIn('code commits: 2', out.getvalue())
        self.assertIn('rework commits: 1', out.getvalue())
        self.assertIn('rate: 50.0%', out.getvalue())

    def test_outside_a_git_repository_fails_with_a_message(self):
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(SystemExit) as raised:
                rework.main(['HEAD~1..HEAD', '--cwd', other])
        self.assertIn('git', str(raised.exception.code))


if __name__ == '__main__':
    unittest.main()

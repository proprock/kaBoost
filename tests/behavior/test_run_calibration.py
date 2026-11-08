import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_calibration as runner  # noqa: E402


def git(*args, cwd):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@invalid', *args], cwd=cwd,
                          check=True, capture_output=True, text=True).stdout


class PrepareTests(unittest.TestCase):
    def test_toolkit_files_are_part_of_the_base_commit(self):
        """The judge and files_changed see only the agent's changes, not the injected core rules (KB-234)."""
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / 'source'
            source.mkdir()
            git('init', '--quiet', cwd=source)
            (source / 'CLAUDE.md').write_text('# Project\n', encoding='utf-8')
            git('add', '-A', cwd=source)
            git('commit', '--quiet', '-m', 'base', cwd=source)
            (source / 'fix.txt').write_text('fix\n', encoding='utf-8')
            git('add', '-A', cwd=source)
            git('commit', '--quiet', '-m', 'fix', cwd=source)
            core = temp / 'rules.md'
            core.write_text('# Rules\n', encoding='utf-8')
            checkout = temp / 'checkout'
            task = {'repo': str(source), 'fix': git('rev-parse', 'HEAD', cwd=source).strip(), 'prep': None}
            runner.prepare(task, checkout, dict(os.environ), core)
            self.assertEqual(git('status', '--porcelain', cwd=checkout), '')
            self.assertEqual(git('show', 'HEAD:.claude/engineering-rules.md', cwd=checkout), '# Rules\n')
            self.assertIn('@.claude/engineering-rules.md', git('show', 'HEAD:CLAUDE.md', cwd=checkout))


if __name__ == '__main__':
    unittest.main()

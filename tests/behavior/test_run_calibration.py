import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


class ModelTests(unittest.TestCase):
    """The model is an option, so tasks can be calibrated on a cheaper model (KB-251)."""

    def model_after(self, command):
        return command[command.index('--model') + 1]

    def test_session_command_passes_the_model(self):
        command = runner.session_command('prompt', 'claude-haiku-5-5', [])
        self.assertEqual(self.model_after(command), 'claude-haiku-5-5')

    def test_judge_command_passes_the_model(self):
        self.assertEqual(self.model_after(runner.judge_command('claude-haiku-5-5')), 'claude-haiku-5-5')

    def dry_run(self, *extra):
        with tempfile.TemporaryDirectory() as temp:
            tasks = Path(temp) / 'tasks.json'
            tasks.write_text('[{"id": "t1", "prep": null}, {"id": "t2", "prep": null}]', encoding='utf-8')
            output = Path(temp) / 'out'
            printed = io.StringIO()
            with mock.patch.object(runner.subprocess, 'run', side_effect=AssertionError('no calls')), \
                    mock.patch.object(runner.pilot, 'command', side_effect=AssertionError('no calls')), \
                    contextlib.redirect_stdout(printed):
                runner.main([str(output), '--tasks', str(tasks), '--n', '5', '--dry-run', *extra])
            self.assertFalse(output.exists())
        return printed.getvalue()

    def test_dry_run_prints_the_default_model_and_calls_nothing(self):
        printed = self.dry_run()
        self.assertIn(runner.pilot.MODEL, printed)
        self.assertIn('10 sessions', printed)

    def test_dry_run_prints_the_chosen_model(self):
        self.assertIn('claude-haiku-5-5', self.dry_run('--model', 'claude-haiku-5-5'))


if __name__ == '__main__':
    unittest.main()

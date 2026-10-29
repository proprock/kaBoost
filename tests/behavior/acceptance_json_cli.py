"""Independent Large-pilot CLI contract check against an isolated checkout.

Usage: python3 acceptance_json_cli.py /path/to/candidate-checkout
Keep this evaluator outside the agent's trial checkout.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKOUT = Path(sys.argv.pop(1)).resolve()


class JsonCliAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kaboost-cli-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'checkout'
        shutil.copytree(CHECKOUT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def run_cli(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(self.root / 'scripts' / script), *arguments],
            cwd=self.root, capture_output=True, text=True, timeout=30,
        )

    def test_success_and_default_compatibility(self):
        for script, text in (('build.py', '8 package files built'),
                             ('validate.py', 'Validation passed: 8 generated files')):
            with self.subTest(script=script):
                plain = self.run_cli(script)
                self.assertEqual((plain.returncode, plain.stdout.strip()), (0, text))
                result = self.run_cli(script, '--json')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {'ok': True, 'files': 8})
                if script == 'build.py':
                    checked = self.run_cli(script, '--check', '--json')
                    self.assertEqual(checked.returncode, 0, checked.stderr)
                    self.assertEqual(json.loads(checked.stdout), {'ok': True, 'files': 8})

    def test_expected_failure(self):
        manifest = self.root / 'toolkit.json'
        manifest.write_text('{invalid json', encoding='utf-8')
        for script in ('build.py', 'validate.py'):
            with self.subTest(script=script):
                plain = self.run_cli(script)
                self.assertNotEqual(plain.returncode, 0)
                self.assertTrue(plain.stderr.strip())
                result = self.run_cli(script, '--json')
                self.assertEqual(result.returncode, plain.returncode)
                data = json.loads(result.stdout)
                self.assertEqual(set(data), {'ok', 'error'})
                self.assertIs(data['ok'], False)
                self.assertIsInstance(data['error'], str)
                self.assertTrue(data['error'].strip())

    def test_existing_unknown_argument_behavior(self):
        # The baseline validate CLI ignores extra arguments. The build CLI
        # rejects them through argparse; the opt-in mode must preserve both.
        plain_validate = self.run_cli('validate.py')
        unknown_validate = self.run_cli('validate.py', '--unrecognized')
        self.assertEqual(unknown_validate.returncode, plain_validate.returncode)
        self.assertEqual(unknown_validate.stdout, plain_validate.stdout)
        unknown_build = self.run_cli('build.py', '--unrecognized')
        self.assertEqual(unknown_build.returncode, 2)


if __name__ == '__main__':
    unittest.main()

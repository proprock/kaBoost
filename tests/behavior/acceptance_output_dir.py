"""Independent holdout check for an opt-in --output-dir option on scripts/build.py.

Usage: python3 acceptance_output_dir.py /path/to/candidate-checkout
Keep this evaluator outside the agent's trial checkout. The existing contracts it
checks are discoverable from build.py itself, validate.py (a caller), and the
packaging tests; the prompt only asks to preserve behavior in general terms.
"""
import filecmp
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKOUT = Path(sys.argv.pop(1)).resolve()


class OutputDirAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kaboost-outdir-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'checkout'
        shutil.copytree(CHECKOUT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.out = self.base / 'out'

    def build(self, *arguments):
        return subprocess.run([sys.executable, str(self.root / 'scripts' / 'build.py'), *arguments],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def tree(self, base):
        return sorted(p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file())

    def test_default_behavior_unchanged(self):
        checked = self.build('--check')
        self.assertEqual((checked.returncode, checked.stdout.strip()), (0, '8 package files verified'))
        built = self.build()
        self.assertEqual((built.returncode, built.stdout.strip()), (0, '8 package files built'))
        validated = subprocess.run([sys.executable, str(self.root / 'scripts' / 'validate.py')],
                                   cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual((validated.returncode, validated.stdout.strip()), (0, 'Validation passed: 8 generated files'))

    def test_output_dir_matches_committed_package(self):
        committed = self.root / 'plugins' / 'kaboost'
        before = {p: p.read_bytes() for p in committed.rglob('*') if p.is_file()}
        result = self.build('--output-dir', str(self.out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tree(self.out), self.tree(committed))
        for name in self.tree(committed):
            self.assertTrue(filecmp.cmp(self.out / name, committed / name, shallow=False), name)
        self.assertEqual({p: p.read_bytes() for p in committed.rglob('*') if p.is_file()}, before)

    def test_check_uses_output_dir(self):
        self.assertEqual(self.build('--output-dir', str(self.out)).returncode, 0)
        self.assertEqual(self.build('--output-dir', str(self.out), '--check').returncode, 0)
        (self.out / 'LICENSE').write_text('tampered', encoding='utf-8')
        self.assertNotEqual(self.build('--output-dir', str(self.out), '--check').returncode, 0)
        missing = self.base / 'missing'
        self.assertNotEqual(self.build('--output-dir', str(missing), '--check').returncode, 0)
        self.assertFalse(missing.exists())

    def test_unknown_files_in_output_dir_are_refused(self):
        self.out.mkdir()
        (self.out / 'notes.txt').write_text('user data', encoding='utf-8')
        result = self.build('--output-dir', str(self.out))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.out / 'notes.txt').read_text(encoding='utf-8'), 'user data')

    @unittest.skipIf(sys.platform == 'win32', 'symlink privilege differs on Windows')
    def test_symlinked_output_dir_is_refused(self):
        real = self.base / 'real'
        real.mkdir()
        self.out.symlink_to(real, target_is_directory=True)
        self.assertNotEqual(self.build('--output-dir', str(self.out)).returncode, 0)
        self.assertEqual(list(real.iterdir()), [])

    def test_python_api_shape_is_preserved(self):
        code = ('import sys; sys.path.insert(0, "scripts"); from pathlib import Path; import build; '
                'root = Path(".").resolve(); '
                'assert build.build(root, True) == 8; '
                'result = build.expected_files(root); '
                'assert isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict)')
        result = subprocess.run([sys.executable, '-c', code], cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_arguments_still_rejected(self):
        self.assertNotEqual(self.build('--bogus').returncode, 0)


if __name__ == '__main__':
    unittest.main()

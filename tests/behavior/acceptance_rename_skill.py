"""Independent holdout check for renaming the `verification` skill to `verify-completion`.

Usage: python3 acceptance_rename_skill.py /path/to/candidate-checkout
Keep this evaluator outside the agent's trial checkout. References to the old name
are discoverable with a repository search; the committed generated package must be
rebuilt and consistent, and the skill's behavior text must not change.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

CHECKOUT = Path(sys.argv.pop(1)).resolve()
ORIGINAL_COMMIT = 'b1d3f01c9884468b8b75ec913eebb5f5ec611f1d'
OLD, NEW = 'verification', 'verify-completion'
# Current, non-historical locations. Evidence records and decision history may keep the old name.
LIVE = ('README.md', 'toolkit.json', 'scripts', 'skills', 'plugins', 'adapters', 'examples', 'tests/packaging',
        '.claude-plugin', '.github', 'core', 'workflows')
STALE = re.compile(r'kaboost:verification|skills/verification|name: verification|"verification"')


class RenameAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kaboost-rename-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'checkout'
        shutil.copytree(CHECKOUT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def run_py(self, *arguments):
        return subprocess.run([sys.executable, *arguments], cwd=self.root, capture_output=True, text=True, timeout=120)

    def test_skill_directory_and_name(self):
        self.assertFalse((self.root / 'skills' / OLD).exists())
        skill = (self.root / 'skills' / NEW / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill.startswith(f'---\nname: {NEW}\n'))

    def test_skill_text_otherwise_unchanged(self):
        original = subprocess.run(['git', 'show', f'{ORIGINAL_COMMIT}:skills/{OLD}/SKILL.md'], cwd=CHECKOUT,
                                  capture_output=True, text=True, check=True).stdout
        expected = original.replace(f'name: {OLD}\n', f'name: {NEW}\n', 1)
        self.assertEqual((self.root / 'skills' / NEW / 'SKILL.md').read_text(encoding='utf-8'), expected)

    def test_manifest_lists_new_name_once(self):
        import json
        skills = json.loads((self.root / 'toolkit.json').read_text(encoding='utf-8'))['skills']
        self.assertEqual(sorted(skills), sorted(['project-context', 'systematic-debugging', NEW]))

    def test_generated_package_is_rebuilt_and_consistent(self):
        result = self.run_py('scripts/build.py', '--check')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / 'plugins/kaboost/skills' / NEW / 'SKILL.md').is_file())
        self.assertFalse((self.root / 'plugins/kaboost/skills' / OLD).exists())

    def test_validation_and_packaging_tests_pass(self):
        self.assertEqual(self.run_py('scripts/validate.py').returncode, 0)
        result = self.run_py('-m', 'unittest', 'discover', '-s', 'tests/packaging')
        self.assertEqual(result.returncode, 0, result.stderr[-800:])

    def test_no_stale_references_in_live_files(self):
        offenders = []
        for entry in LIVE:
            base = self.root / entry
            for path in ([base] if base.is_file() else base.rglob('*') if base.exists() else []):
                if path.is_file() and not path.is_symlink():
                    try:
                        text = path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        continue
                    if STALE.search(text):
                        offenders.append(path.relative_to(self.root).as_posix())
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()

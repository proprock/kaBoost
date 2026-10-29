import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_codex import build


class CodexPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex package test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.output = self.root / 'adapters/codex/package/ai-dev-toolkit'

    def test_package_contains_canonical_skills_and_resolvable_workflow(self):
        build(self.root)
        manifest = json.loads((self.root / 'toolkit.json').read_text())
        plugin = json.loads((self.output / 'plugin.json').read_text())
        legacy = json.loads((self.output / '.codex-plugin/plugin.json').read_text())
        self.assertEqual((plugin['name'], plugin['version']), (manifest['name'], manifest['version']))
        self.assertEqual((legacy['name'], legacy['version']), (plugin['name'], plugin['version']))
        self.assertEqual(legacy['interface'], plugin['extensions']['com.openai']['interface'])
        for name in manifest['skills']:
            self.assertEqual((self.output / 'skills' / name / 'SKILL.md').read_bytes(),
                             (self.root / 'skills' / name / 'SKILL.md').read_bytes())
        self.assertTrue((self.output / 'skills/project-context/../../workflows/adaptive.md').is_file())
        build(self.root, check=True)

    def test_tampering_and_unexpected_files_are_detected(self):
        build(self.root)
        skill = self.output / 'skills/verification/SKILL.md'
        skill.write_text('tampered', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'stale'):
            build(self.root, check=True)
        build(self.root)
        extra = self.output / 'local.txt'
        extra.write_text('preserve', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unexpected output'):
            build(self.root)
        self.assertEqual(extra.read_text(), 'preserve')

    def test_version_mismatch_is_rejected(self):
        path = self.root / 'toolkit.json'
        manifest = json.loads(path.read_text())
        manifest['version'] = '0.2.0'
        path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'name/version mismatch'):
            build(self.root)

    @unittest.skipIf(sys.platform == 'win32', 'Symlink creation may require privileges')
    def test_symlinks_in_output_are_rejected(self):
        build(self.root)
        link = self.output / 'linked'
        link.symlink_to(self.root / 'core', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink output'):
            build(self.root)
        self.assertTrue(link.is_symlink())

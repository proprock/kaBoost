import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from build import build
from validate import validate


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kaboost path test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()/'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    def test_build_is_repeatable_and_preserves_user_files(self):
        sentinel = self.root/'user-settings.json'
        sentinel.write_text('user owned', encoding='utf-8')
        build(self.root)
        first = {p.relative_to(self.root): p.read_bytes() for p in (self.root/'plugins').rglob('*') if p.is_file()}
        build(self.root)
        self.assertTrue(all((self.root/p).read_bytes() == content for p, content in first.items()))
        self.assertEqual(sentinel.read_text(), 'user owned')
        validate(self.root)

    def test_tampering_is_detected_and_rebuild_repairs_it(self):
        path = self.root/'plugins/ai-dev-toolkit/skills/verification/SKILL.md'
        path.write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)
        build(self.root)
        validate(self.root)

    def test_unexpected_package_file_is_not_deleted(self):
        path = self.root/'plugins/ai-dev-toolkit/local.txt'
        path.write_text('local override', encoding='utf-8')
        with self.assertRaises(ValueError):
            build(self.root)
        self.assertEqual(path.read_text(), 'local override')

    def test_traversal_source_is_rejected(self):
        path = self.root/'toolkit.json'
        data = json.loads(path.read_text())
        data['core'] = '../outside.md'
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            build(self.root)

    def test_manifest_version_drift_is_rejected(self):
        path = self.root/'toolkit.json'
        data = json.loads(path.read_text())
        data['version'] = '0.2.0'
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            build(self.root)

    @unittest.skipIf(sys.platform == 'win32', 'Symlink creation may require privileges')
    def test_symlink_output_is_rejected(self):
        output = self.root/'plugins/ai-dev-toolkit'
        shutil.rmtree(output)
        output.symlink_to(self.root/'core', target_is_directory=True)
        with self.assertRaises(ValueError):
            build(self.root)

    def test_duplicate_skills_are_rejected(self):
        path = self.root/'toolkit.json'
        data = json.loads(path.read_text())
        data['skills'].append(data['skills'][0])
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_invalid_frontmatter_is_rejected(self):
        path = self.root/'skills/verification/SKILL.md'
        path.write_text('---\nname: wrong\n---\nBody', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_broken_relative_reference_is_rejected(self):
        path = self.root/'skills/verification/SKILL.md'
        path.write_text(path.read_text() + '\n[missing](references/missing.md)\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

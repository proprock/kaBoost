import json
from pathlib import Path
import re
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
        path = self.root/'plugins/kaboost/skills/verification/SKILL.md'
        path.write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)
        build(self.root)
        validate(self.root)

    def test_unexpected_package_file_is_not_deleted(self):
        path = self.root/'plugins/kaboost/local.txt'
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

    def test_noncanonical_stable_versions_are_rejected(self):
        path = self.root/'toolkit.json'
        data = json.loads(path.read_text())
        for version in ('01.2.3', '1.02.3', '1.2.03', '١.2.3', '1.2.3-rc.1', '1.2.3+build'):
            with self.subTest(version=version):
                data['version'] = version
                path.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'stable SemVer'):
                    validate(self.root)

    def test_external_actions_are_pinned_by_commit_sha(self):
        files = sorted((ROOT/'.github/workflows').glob('*.yml')) + sorted((ROOT/'init/features').glob('*.yml'))
        for path in files:
            for line in path.read_text(encoding='utf-8').splitlines():
                match = re.match(r'\s*(?:-\s*)?uses:\s*(\S+)', line)
                if match and not match[1].startswith('./'):
                    with self.subTest(file=path.name, action=match[1]):
                        self.assertRegex(match[1], r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$')

    def test_init_feature_workflows_follow_the_repository_pins(self):
        # Dependabot updates only .github/workflows; init features copy those pins, so a bump fails here until both move.
        def pins(paths):
            found = {}
            for path in paths:
                for match in re.finditer(r'uses:\s*([\w.-]+/[\w./-]+)@(\S+)', path.read_text(encoding='utf-8')):
                    found.setdefault(match[1], {}).setdefault(match[2], path.name)
            return found
        repository = pins(sorted((ROOT/'.github/workflows').glob('*.yml')))
        for action, shas in pins(sorted((ROOT/'init/features').glob('*.yml'))).items():
            if action in repository:
                with self.subTest(action=action):
                    self.assertEqual(set(shas), set(repository[action]), f'{action}: features {shas}, workflows {repository[action]}')

    def test_release_documents_must_name_the_current_release(self):
        version = json.loads((self.root/'toolkit.json').read_text())['version']
        for name in ('README.md', 'docs/compatibility.md', 'docs/release-gate-assessment.md', 'docs/migration.md'):
            with self.subTest(document=name):
                path = self.root/name
                original = path.read_text(encoding='utf-8')
                path.write_text(original.replace(f'`v{version}`', '`v0.0.9`'), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, f'{name}.*v{re.escape(version)}'):
                    validate(self.root)
                path.write_text(original, encoding='utf-8')

    @unittest.skipIf(sys.platform == 'win32', 'Symlink creation may require privileges')
    def test_symlink_output_is_rejected(self):
        output = self.root/'plugins/kaboost'
        shutil.rmtree(output)
        output.symlink_to(self.root/'core', target_is_directory=True)
        with self.assertRaises(ValueError):
            build(self.root)

    @unittest.skipIf(sys.platform == 'win32', 'Symlink creation may require privileges')
    def test_symlink_above_the_root_is_accepted(self):
        link = self.root.parent/'linked-repo'
        link.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(build(link, check=True), build(self.root, check=True))
        validate(link)

    def test_duplicate_skills_are_rejected(self):
        path = self.root/'toolkit.json'
        data = json.loads(path.read_text())
        data['skills'].append(data['skills'][0])
        path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_package_contains_commands(self):
        data = json.loads((self.root/'toolkit.json').read_text())
        self.assertIn('help', data['commands'])
        for name in data['commands']:
            self.assertTrue((self.root/f'plugins/kaboost/commands/{name}.md').is_file())

    def test_unlisted_command_is_rejected(self):
        (self.root/'commands/extra.md').write_text('---\ndescription: Extra\n---\nBody', encoding='utf-8')
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_command_without_description_is_rejected(self):
        path = self.root/'commands/help.md'
        path.write_text('---\nargument-hint: x\n---\nBody', encoding='utf-8')
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

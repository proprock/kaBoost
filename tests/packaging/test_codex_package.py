import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_codex import build
from validate_codex import validate


class CodexPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex package test ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.output = self.root / 'adapters/codex/package/kaboost'

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

    def test_init_skills_are_explicit_only_and_script_runs_from_the_package(self):
        build(self.root)
        manifest = json.loads((self.root / 'toolkit.json').read_text())
        self.assertEqual(manifest['codex_skills'], ['kaboost-init', 'kaboost-init-global'])
        for name in manifest['codex_skills']:
            skill = self.output / 'skills' / name
            self.assertIn('allow_implicit_invocation: false', (skill / 'agents/openai.yaml').read_text())
            self.assertIn('--targets codex', (skill / 'SKILL.md').read_text())
            self.assertTrue((skill / '../../init/kaboost_init.py').is_file())
        repo, home = self.root.parent / 'work', self.root.parent / 'home'
        repo.mkdir()
        (home / '.codex').mkdir(parents=True)
        script = str(self.output / 'init/kaboost_init.py')
        base = [sys.executable, '-I', script]
        for scope, ids in (('repo', 'core-rules'), ('global', 'core-rules-global')):
            args = ['--scope', scope, '--targets', 'codex', '--root', str(repo), '--home', str(home)]
            subprocess.run(base + ['apply', '--ids', ids, '--yes'] + args, check=True, capture_output=True)
        self.assertIn('Engineering rules', (repo / 'AGENTS.md').read_text())
        self.assertIn('Engineering rules', (home / '.codex/AGENTS.md').read_text())
        self.assertFalse((repo / 'CLAUDE.md').exists() or (repo / '.claude').exists())

    def test_implicit_invocation_policy_is_required(self):
        path = self.root / 'adapters/codex/skills/kaboost-init/agents/openai.yaml'
        path.write_text('policy:\n  allow_implicit_invocation: true\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'disable implicit invocation'):
            build(self.root)

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

    def test_catalog_identity_source_and_policy_are_validated(self):
        path = self.root / 'adapters/codex/.agents/plugins/marketplace.json'
        original = json.loads(path.read_text())
        validate(self.root)
        for field, value in (('name', 'wrong'), ('source', {'source': 'local', 'path': '../wrong'}),
                             ('policy', {'installation': 'UNAVAILABLE', 'authentication': 'ON_INSTALL'})):
            with self.subTest(field=field):
                data = json.loads(json.dumps(original))
                data['plugins'][0][field] = value
                path.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'Codex marketplace'):
                    validate(self.root)

    def test_validation_detects_stale_codex_package(self):
        (self.output / 'plugin.json').write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Generated Codex files are stale'):
            validate(self.root)

    @unittest.skipIf(sys.platform == 'win32', 'Symlink creation may require privileges')
    def test_symlinks_in_output_are_rejected(self):
        build(self.root)
        link = self.output / 'linked'
        link.symlink_to(self.root / 'core', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink output'):
            build(self.root)
        self.assertTrue(link.is_symlink())

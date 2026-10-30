import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'init'))
import kaboost_init as init  # noqa: E402


class InitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.repo, self.home = base / 'repo', base / 'home'
        (self.home / '.claude').mkdir(parents=True)
        self.repo.mkdir()

    def call(self, *args, scope='repo'):
        out = io.StringIO()
        argv = [args[0], '--scope', scope, '--root', str(self.repo), '--home', str(self.home), *args[1:]]
        with contextlib.redirect_stdout(out):
            self.assertEqual(init.main(argv), 0)
        return json.loads(out.getvalue())

    def features(self, scope='repo', *extra):
        data = self.call('status', *extra, scope=scope)
        return {f['id']: f for f in data['features']}

    def test_status_shows_only_relevant_features(self):
        self.assertNotIn('python-toolchain', self.features())
        (self.repo / 'pyproject.toml').write_text('[project]\n')
        features = self.features()
        self.assertEqual(features['python-toolchain']['state'], 'disabled')
        self.assertNotIn('windows-notes', features)
        self.assertIn('windows-notes', self.features('repo', '--all'))

    def test_preview_writes_nothing(self):
        result = self.call('apply', '--ids', 'core-rules')
        self.assertFalse(result['written'])
        self.assertTrue(result['changes'])
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_apply_is_idempotent_and_marks_state(self):
        self.call('apply', '--ids', 'core-rules,agents-index', '--yes')
        self.assertTrue((self.repo / '.claude/engineering-rules.md').is_file())
        self.assertIn('@.claude/engineering-rules.md', (self.repo / 'CLAUDE.md').read_text())
        self.assertEqual(self.features()['core-rules']['state'], 'enabled')
        again = self.call('apply', '--ids', 'core-rules,agents-index', '--yes')
        self.assertEqual(again['changes'], [])

    def restore_case(self, original, name='CLAUDE.md'):
        path = self.repo / name
        if original is not None:
            path.write_bytes(original)
        self.call('apply', '--ids', 'claude-pointer,core-rules', '--yes')
        self.assertNotEqual(path.read_bytes(), original)
        self.call('disable', '--ids', 'claude-pointer,core-rules', '--yes')
        if original is None:
            self.assertFalse(path.exists())
            self.assertFalse((self.repo / '.claude/engineering-rules.md').exists())
        else:
            self.assertEqual(path.read_bytes(), original)

    def test_disable_restores_original_bytes(self):
        cases = {
            'trailing newline': b'# Project\n\nExisting rules.\n',
            'no trailing newline': b'# Project\n\nExisting rules.',
            'crlf': b'# Project\r\n\r\nExisting rules.\r\n',
            'bom': b'\xef\xbb\xbf# Project\n',
            'empty file': b'',
            'missing file': None,
        }
        for label, original in cases.items():
            with self.subTest(label):
                self.setUp()
                self.restore_case(original)

    def test_hand_edited_block_is_not_overwritten(self):
        self.call('apply', '--ids', 'agents-index', '--yes')
        path = self.repo / 'AGENTS.md'
        path.write_text(path.read_text().replace('compact index', 'my own index'))
        skipped = self.call('apply', '--ids', 'agents-index', '--yes')
        self.assertEqual(skipped['report'][0]['result'], 'skipped')
        self.assertIn('my own index', path.read_text())
        self.assertEqual(self.features()['agents-index']['state'], 'drift')
        refused = self.call('disable', '--ids', 'agents-index', '--yes')
        self.assertEqual(refused['report'][0]['result'], 'skipped')
        self.call('apply', '--ids', 'agents-index', '--yes', '--force')
        self.assertEqual(self.features()['agents-index']['state'], 'enabled')

    def test_unmanaged_own_file_is_never_replaced(self):
        (self.repo / 'TODO.md').write_text('mine\n')
        result = self.call('apply', '--ids', 'todo-done', '--yes')
        self.assertEqual(result['report'][0]['result'], 'skipped')
        self.assertEqual((self.repo / 'TODO.md').read_text(), 'mine\n')
        self.assertFalse((self.repo / 'DONE.md').exists())
        self.assertEqual(self.features()['todo-done']['state'], 'conflict')

    def test_damaged_markers_are_refused(self):
        self.call('apply', '--ids', 'agents-index', '--yes')
        path = self.repo / 'AGENTS.md'
        path.write_text(path.read_text().replace('<!-- kaboost:end agents-index:index -->', ''))
        result = self.call('apply', '--ids', 'agents-index', '--yes')
        self.assertEqual(result['report'][0]['result'], 'skipped')
        self.assertEqual(self.features()['agents-index']['state'], 'conflict')

    def test_backup_is_written_next_to_a_modified_file(self):
        (self.repo / 'CLAUDE.md').write_text('mine\n')
        self.call('apply', '--ids', 'claude-pointer', '--yes')
        backups = list(self.repo.glob('CLAUDE.md.kaboost-bak-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'mine\n')

    def test_outdated_block_is_updated_in_place(self):
        self.call('apply', '--ids', 'agents-index', '--yes')
        catalog = init.load_catalog()
        for feature in catalog['features']:
            for edit in feature['edits']:
                if feature['id'] == 'agents-index':
                    edit['version'] = 2
        with mock.patch.object(init, 'load_catalog', return_value=catalog):
            self.assertEqual(self.features()['agents-index']['state'], 'outdated')
            self.call('apply', '--ids', 'agents-index', '--yes')
            self.assertEqual(self.features()['agents-index']['state'], 'enabled')
        self.assertEqual((self.repo / 'AGENTS.md').read_text().count('kaboost:begin'), 1)

    def test_global_scope_targets_existing_tools_only(self):
        self.call('apply', '--ids', 'delegation', '--yes', scope='global')
        self.assertTrue((self.home / '.claude/CLAUDE.md').is_file())
        self.assertFalse((self.home / '.codex').exists())
        self.call('apply', '--ids', 'delegation', '--yes', '--targets', 'codex', scope='global')
        self.assertTrue((self.home / '.codex/AGENTS.md').is_file())
        self.call('disable', '--ids', 'delegation', '--yes', '--targets', 'claude,codex', scope='global')
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())
        self.assertFalse((self.home / '.codex/AGENTS.md').exists())

    def test_global_core_rules_keep_personal_text_and_restore_it(self):
        claude = self.home / '.claude/CLAUDE.md'
        codex_dir = self.home / '.codex'
        codex_dir.mkdir()
        (codex_dir / 'AGENTS.md').write_bytes(b'# Mine\n')
        claude.write_bytes(b'# Personal rules\n\nKeep answers short.')
        original = {claude: claude.read_bytes(), codex_dir / 'AGENTS.md': b'# Mine\n'}
        preview = self.call('apply', '--ids', 'core-rules-global', scope='global')
        self.assertEqual(len(preview['changes']), 2)
        self.assertEqual(claude.read_bytes(), original[claude])
        self.call('apply', '--ids', 'core-rules-global', '--yes', scope='global')
        for path, before in original.items():
            self.assertTrue(path.read_bytes().startswith(before.rstrip(b'\n')))
            self.assertIn(b'Engineering rules', path.read_bytes())
        self.assertEqual(self.features('global')['core-rules-global']['state'], 'enabled')
        self.call('disable', '--ids', 'core-rules-global', '--yes', scope='global')
        for path, before in original.items():
            self.assertEqual(path.read_bytes(), before)

    def test_global_scope_never_touches_the_repository(self):
        self.call('apply', '--ids', 'delegation', '--yes', scope='global')
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_unknown_feature_id_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.call('apply', '--ids', 'no-such-feature')

    def test_catalog_is_consistent(self):
        catalog = init.load_catalog()
        ids = [f['id'] for f in catalog['features']]
        self.assertEqual(len(ids), len(set(ids)))
        for feature in catalog['features']:
            self.assertIn(feature['scope'], ('repo', 'global'))
            for edit in feature['edits']:
                self.assertIn(edit['mode'], ('own', 'append'))
                self.assertTrue(init.body_of(edit).strip())
                self.assertRegex(edit['target'], r'^\{(repo|home)\}/')


if __name__ == '__main__':
    unittest.main()

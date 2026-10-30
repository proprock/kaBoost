import contextlib
import io
import os
import stat
import subprocess
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
        self.assertTrue((self.repo / '.claude/kaboost/core-rules.md').is_file())
        self.assertIn('@.claude/kaboost/core-rules.md', (self.repo / 'CLAUDE.md').read_text())
        self.assertEqual(self.features()['core-rules']['state'], 'enabled')
        again = self.call('apply', '--ids', 'core-rules,agents-index', '--yes')
        self.assertEqual(again['changes'], [])

    def restore_case(self, original, name='CLAUDE.md'):
        path = self.repo / name
        if original is not None:
            path.write_bytes(original)
        self.call('apply', '--ids', 'agents-import,core-rules', '--yes')
        self.assertNotEqual(path.read_bytes(), original)
        self.call('disable', '--ids', 'agents-import,core-rules', '--yes')
        if original is None:
            self.assertFalse(path.exists())
            self.assertFalse((self.repo / '.claude/kaboost/core-rules.md').exists())
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
        self.call('apply', '--ids', 'agents-import', '--yes')
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

    def test_targets_is_a_list_with_all_and_validation(self):
        catalog = init.load_catalog()
        self.assertEqual(init.parse_targets('', catalog), None)
        self.assertEqual(init.parse_targets('codex, claude codex', catalog), ['codex', 'claude'])
        self.assertEqual(init.parse_targets('all', catalog), init.known_tools(catalog))
        with self.assertRaises(SystemExit):
            init.parse_targets('claude,gemini', catalog)
        self.call('apply', '--ids', 'delegation', '--yes', '--targets', 'all', scope='global')
        self.assertTrue((self.home / '.claude/CLAUDE.md').is_file())
        self.assertTrue((self.home / '.codex/AGENTS.md').is_file())

    def test_features_sharing_a_file_are_planned_together(self):
        (self.repo / 'pyproject.toml').write_text('[project]\n')
        path = self.repo / 'AGENTS.md'
        path.write_bytes(b'# Mine\n')
        self.call('apply', '--ids', 'agents-index,python-toolchain,windows-notes', '--yes')
        self.assertEqual(path.read_text().count('kaboost:begin'), 3)
        self.call('disable', '--ids', 'agents-index,python-toolchain,windows-notes', '--yes')
        self.assertEqual(path.read_bytes(), b'# Mine\n')

    def fake_prek(self, ok=True):
        """A prek stand-in on PATH that writes or removes the hook the way prek does."""
        bin_dir = self.repo.parent / 'bin'
        bin_dir.mkdir(exist_ok=True)
        fake = bin_dir / 'prek'
        fake.write_text('#!/bin/sh\n' + ('' if ok else 'exit 3\n') + 'case "$1" in\n'
                        '  install) mkdir -p .git/hooks && echo "# File generated by prek" > .git/hooks/pre-commit;;\n'
                        '  uninstall) rm -f .git/hooks/pre-commit;;\nesac\n')
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        patcher = mock.patch.dict(os.environ, {'PATH': f'{bin_dir}{os.pathsep}{os.environ["PATH"]}'})
        patcher.start()
        self.addCleanup(patcher.stop)

    def git_repo(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        (self.repo / 'pyproject.toml').write_text('[project]\n')

    @unittest.skipIf(os.name == 'nt', 'the stand-in is a shell script')
    def test_git_hook_is_installed_and_removed_with_its_files(self):
        self.git_repo()
        self.fake_prek()
        hook = self.repo / '.git/hooks/pre-commit'
        preview = self.call('apply', '--ids', 'precommit-hooks')
        self.assertEqual(preview['commands'], [{'feature': 'precommit-hooks', 'command': 'prek install'}])
        self.assertFalse(hook.exists())
        self.call('apply', '--ids', 'precommit-hooks', '--yes')
        self.assertTrue(hook.exists())
        self.assertTrue((self.repo / '.pre-commit-config.yaml').exists())
        self.assertEqual(self.features()['precommit-hooks']['state'], 'enabled')
        again = self.call('apply', '--ids', 'precommit-hooks', '--yes')
        self.assertEqual((again['changes'], again['commands']), ([], []))
        self.call('disable', '--ids', 'precommit-hooks', '--yes')
        self.assertFalse(hook.exists())
        self.assertFalse((self.repo / '.pre-commit-config.yaml').exists())

    @unittest.skipIf(os.name == 'nt', 'the stand-in is a shell script')
    def test_failed_hook_install_leaves_nothing_half_done(self):
        self.git_repo()
        self.fake_prek(ok=False)
        out = io.StringIO()
        argv = ['apply', '--scope', 'repo', '--root', str(self.repo), '--home', str(self.home),
                '--ids', 'precommit-hooks', '--yes']
        with contextlib.redirect_stdout(out):
            self.assertEqual(init.main(argv), 1)
        self.assertEqual(json.loads(out.getvalue())['report'][0]['result'], 'failed')
        self.assertFalse((self.repo / '.pre-commit-config.yaml').exists())
        self.assertFalse((self.repo / 'AGENTS.md').exists())

    @unittest.skipIf(os.name == 'nt', 'the stand-in is a shell script')
    def test_foreign_hook_and_missing_tools_are_refused(self):
        self.git_repo()
        hook = self.repo / '.git/hooks/pre-commit'
        hook.parent.mkdir(exist_ok=True)
        hook.write_text('#!/bin/sh\nexit 0\n')
        self.fake_prek()
        result = self.call('apply', '--ids', 'precommit-hooks', '--yes')
        self.assertEqual(result['report'][0]['result'], 'skipped')
        self.assertEqual(hook.read_text(), '#!/bin/sh\nexit 0\n')
        self.assertFalse((self.repo / '.pre-commit-config.yaml').exists())
        hook.unlink()
        with mock.patch.object(init.shutil, 'which', return_value=None):
            result = self.call('apply', '--ids', 'precommit-hooks', '--yes')
        self.assertEqual(result['report'][0]['result'], 'skipped')
        self.assertIn('not installed', result['report'][0]['reason'])
        self.assertFalse((self.repo / '.pre-commit-config.yaml').exists())

    def snapshot(self):
        return {str(p.relative_to(self.repo)): p.read_bytes() for p in sorted(self.repo.rglob('*'))
                if p.is_file() and '.git' not in p.relative_to(self.repo).parts}

    @unittest.skipIf(os.name == 'nt', 'the prek stand-in is a shell script')
    def test_every_repository_feature_applies_and_disables_to_the_original_files(self):
        self.git_repo()
        self.fake_prek()
        (self.repo / 'pyproject.toml').write_text('[project]\nversion = "1.2.0"\n')
        (self.repo / '.mcp.json').write_text('{}\n')
        (self.repo / 'AGENTS.md').write_bytes(b'# Mine\r\n')
        (self.repo / 'Makefile').write_bytes(b'all:\n\ttrue')
        before = self.snapshot()
        catalog = init.load_catalog()
        ids = ','.join(f['id'] for f in catalog['features'] if f['scope'] == 'repo')
        self.assertEqual({f['id'] for f in catalog['features'] if f['scope'] == 'repo'},
                         set(self.features('repo', '--all')))
        for targets in ('claude,codex',):
            preview = self.call('apply', '--ids', ids, '--targets', targets)
            self.assertFalse(preview['written'])
            self.assertEqual(self.snapshot(), before)
            applied = self.call('apply', '--ids', ids, '--yes', '--targets', targets)
            self.assertEqual([r['result'] for r in applied['report'] if r['result'] == 'skipped'], [])
            self.assertEqual(self.call('apply', '--ids', ids, '--yes', '--targets', targets)['changes'], [])
            states = {f: v['state'] for f, v in self.features('repo', '--all', '--targets', targets).items()}
            self.assertEqual(set(states.values()), {'enabled'}, states)
            self.call('disable', '--ids', ids, '--yes', '--targets', targets)
            after = {k: v for k, v in self.snapshot().items() if not k.endswith('.kaboost-bak-')
                     and '.kaboost-bak-' not in k}
            self.assertEqual(after, before)

    def test_skill_files_keep_a_valid_header_and_split_by_tool(self):
        self.call('apply', '--ids', 'review-skills', '--yes', '--targets', 'claude')
        claude = self.repo / '.claude/skills/kaboost-pr-summary/SKILL.md'
        text = claude.read_text()
        self.assertTrue(text.startswith('---\nname: kaboost-pr-summary\n'))
        self.assertIn('disable-model-invocation: true', text.split('---')[1])
        self.assertLess(text.index('kaboost:begin'), text.index('# Pull request summary'))
        self.assertGreater(text.index('kaboost:begin'), text.index('\n---\n'))
        self.assertFalse((self.repo / '.agents').exists())
        self.call('apply', '--ids', 'review-skills', '--yes', '--targets', 'codex')
        codex = self.repo / '.agents/skills/kaboost-pr-summary'
        self.assertTrue((codex / 'SKILL.md').read_text().startswith('---\nname: kaboost-pr-summary\n'))
        self.assertNotIn('disable-model-invocation', (codex / 'SKILL.md').read_text())
        self.assertIn('allow_implicit_invocation: false', (codex / 'agents/openai.yaml').read_text())
        self.call('disable', '--ids', 'review-skills', '--yes', '--targets', 'claude,codex')
        self.assertEqual(self.snapshot(), {})

    def test_skill_bodies_are_identical_for_both_tools(self):
        for key in ('pr-summary', 'coverage-improvement', 'release-review'):
            claude = init.split_front((init.HERE / f'features/skill-{key}.claude.md').read_text())
            codex = init.split_front((init.HERE / f'features/skill-{key}.codex.md').read_text())
            self.assertEqual(claude[1], codex[1])

    def test_version_check_script_detects_a_mismatch(self):
        (self.repo / 'pyproject.toml').write_text('[project]\nversion = "1.2.0"\n')
        (self.repo / 'CHANGELOG.md').write_text('# Changelog\n\n## [Unreleased]\n\n## [1.2.0] - 2026-01-31\n')
        self.call('apply', '--ids', 'release-check', '--yes')
        script = self.repo / 'scripts/kaboost_check_version.py'
        run = lambda: subprocess.run([sys.executable, '-I', str(script), str(self.repo)], capture_output=True, text=True)
        self.assertEqual(run().returncode, 0)
        (self.repo / 'pyproject.toml').write_text('[project]\nversion = "1.3.0"\n')
        result = run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('1.3.0', result.stderr)

    def test_relevance_of_new_features(self):
        self.assertNotIn('ci-python', self.features())
        self.assertNotIn('tool-selection-eval', self.features())
        (self.repo / '.mcp.json').write_text('{}')
        (self.repo / 'pyproject.toml').write_text('[project]\n')
        features = self.features()
        for fid in ('ci-python', 'release-check', 'precommit-hooks', 'tool-selection-eval', 'coverage-review', 'review-skills'):
            self.assertIn(fid, features)

    def test_repo_scope_splits_files_by_tool(self):
        self.call('apply', '--ids', 'core-rules,agents-index', '--yes', '--targets', 'claude')
        self.assertTrue((self.repo / '.claude/kaboost/core-rules.md').is_file())
        self.assertNotIn('Engineering rules', (self.repo / 'AGENTS.md').read_text())
        self.assertEqual(self.features('repo', '--targets', 'claude')['core-rules']['state'], 'enabled')
        self.assertEqual(self.features('repo', '--targets', 'codex')['core-rules']['state'], 'disabled')
        self.assertNotIn('agents-import', self.features('repo', '--targets', 'codex'))
        self.call('apply', '--ids', 'core-rules', '--yes', '--targets', 'codex')
        self.assertIn('Engineering rules', (self.repo / 'AGENTS.md').read_text())
        self.call('disable', '--ids', 'core-rules', '--yes', '--targets', 'codex')
        self.assertNotIn('Engineering rules', (self.repo / 'AGENTS.md').read_text())
        self.assertTrue((self.repo / '.claude/kaboost/core-rules.md').is_file())

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
                if edit.get('kind') == 'git-hook':
                    self.assertTrue(edit['command'])
                    continue
                self.assertIn(edit['mode'], ('own', 'append'))
                if edit.get('frontmatter'):
                    self.assertEqual(edit['mode'], 'own')
                    self.assertTrue(init.parts(edit)[0].startswith('---\n'))
                self.assertTrue(init.body_of(edit).strip())
                self.assertRegex(edit['target'], r'^\{(repo|home)\}/')


if __name__ == '__main__':
    unittest.main()

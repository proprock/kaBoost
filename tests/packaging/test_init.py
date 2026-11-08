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

    def call_with_client_homes(self, *args, env):
        # No --home: the engine reads the clients' own variables, as /kaboost:init-global does.
        out = io.StringIO()
        with (mock.patch.dict(os.environ, env), mock.patch.object(init.Path, 'home', return_value=self.home),
              contextlib.redirect_stdout(out)):
            self.assertEqual(init.main([args[0], '--scope', 'global', '--root', str(self.repo), *args[1:]]), 0)
        return json.loads(out.getvalue())

    def test_global_scope_follows_claude_config_dir_and_codex_home(self):
        claude_dir, codex_dir = self.home.parent / 'claude-config', self.home.parent / 'codex-home'
        claude_dir.mkdir()
        codex_dir.mkdir()
        env = {'CLAUDE_CONFIG_DIR': str(claude_dir), 'CODEX_HOME': str(codex_dir)}
        preview = self.call_with_client_homes('apply', '--ids', 'delegation', env=env)
        self.assertEqual(sorted(c['file'] for c in preview['changes']),
                         sorted([str(claude_dir / 'CLAUDE.md'), str(codex_dir / 'AGENTS.md')]))
        self.call_with_client_homes('apply', '--ids', 'delegation', '--yes', env=env)
        self.assertIn('kaboost:begin', (claude_dir / 'CLAUDE.md').read_text())
        self.assertIn('kaboost:begin', (codex_dir / 'AGENTS.md').read_text())
        self.assertFalse((self.home / '.claude/CLAUDE.md').exists())
        status = self.call_with_client_homes('status', env=env)
        delegation = next(f for f in status['features'] if f['id'] == 'delegation')
        self.assertEqual(delegation['state'], 'enabled')

    def test_explicit_home_overrides_the_client_variables(self):
        other = self.home.parent / 'claude-config'
        other.mkdir()
        with mock.patch.dict(os.environ, {'CLAUDE_CONFIG_DIR': str(other)}):
            self.call('apply', '--ids', 'delegation', '--yes', scope='global')
        self.assertTrue((self.home / '.claude/CLAUDE.md').is_file())
        self.assertFalse((other / 'CLAUDE.md').exists())

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
        script = bin_dir / 'prek_stand_in.py'
        script.write_text('import sys\nfrom pathlib import Path\n' + ('' if ok else 'sys.exit(3)\n') +
                          "hook = Path('.git/hooks/pre-commit')\n"
                          "if sys.argv[1] == 'install':\n"
                          "    hook.parent.mkdir(parents=True, exist_ok=True)\n"
                          "    hook.write_text('# File generated by prek\\n')\n"
                          "elif sys.argv[1] == 'uninstall':\n"
                          "    hook.unlink(missing_ok=True)\n")
        if os.name == 'nt':
            (bin_dir / 'prek.cmd').write_text(f'@"{sys.executable}" "%~dp0prek_stand_in.py" %*\r\n')
        else:
            fake = bin_dir / 'prek'
            fake.write_text(f'#!{sys.executable}\n' + script.read_text())
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
        patcher = mock.patch.dict(os.environ, {'PATH': f'{bin_dir}{os.pathsep}{os.environ["PATH"]}'})
        patcher.start()
        self.addCleanup(patcher.stop)

    def git_repo(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        (self.repo / 'pyproject.toml').write_text('[project]\n')

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

    def test_tdd_commits_feature_ships_the_rule_and_the_audit_script(self):
        self.assertEqual(self.features()['tdd-commits']['state'], 'disabled')
        self.call('apply', '--ids', 'tdd-commits', '--yes')
        self.assertIn('TDD: red', (self.repo / 'AGENTS.md').read_text(encoding='utf-8'))
        script = self.repo / 'scripts/kaboost_audit_tdd.py'
        source = (init.HERE / 'features/audit_tdd.py').read_text(encoding='utf-8').replace('\r\n', '\n')
        self.assertIn(source, script.read_text(encoding='utf-8').replace('\r\n', '\n'))
        result = subprocess.run([sys.executable, '-I', str(script), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('scripts/kaboost_audit_tdd.py', result.stdout)

    def test_rust_pack_is_offered_for_cargo_projects_and_coexists_with_python(self):
        self.assertNotIn('rust-toolchain', self.features())
        self.assertNotIn('ci-rust', self.features())
        (self.repo / 'Cargo.toml').write_text('[package]\nname = "x"\n')
        (self.repo / 'pyproject.toml').write_text('[project]\n')
        (self.repo / 'AGENTS.md').write_bytes(b'# Mine\n')
        features = self.features()
        self.assertEqual(features['rust-toolchain']['group'], 'Rust')
        self.assertNotEqual(features['ci-rust']['title'], features['ci-python']['title'])
        ids = 'rust-toolchain,ci-rust,ci-python'
        self.call('apply', '--ids', ids, '--yes')
        self.assertIn('cargo clippy', (self.repo / 'AGENTS.md').read_text(encoding='utf-8'))
        workflow = (self.repo / '.github/workflows/kaboost-ci-rust.yml').read_text(encoding='utf-8')
        self.assertIn("!contains(github.event.head_commit.message, 'TDD: red')", workflow)
        self.assertIn('cargo test', workflow)
        self.assertTrue((self.repo / '.github/workflows/kaboost-ci.yml').is_file())
        self.assertTrue(all(self.features()[f]['state'] == 'enabled' for f in ids.split(',')))
        self.call('disable', '--ids', ids, '--yes')
        self.assertEqual((self.repo / 'AGENTS.md').read_bytes(), b'# Mine\n')
        self.assertFalse((self.repo / '.github/workflows/kaboost-ci-rust.yml').exists())

    def test_ci_workflows_install_the_system_packages_a_project_lists(self):
        for body in ('ci-rust.yml', 'ci-python.yml'):
            text = (init.HERE / 'features' / body).read_text(encoding='utf-8')
            with self.subTest(body=body):
                self.assertIn('.github/apt-packages.txt', text)
                self.assertLess(text.index('apt-get install'), text.index('uv sync' if 'python' in body else 'cargo clippy'))

    def test_todo_done_rules_keep_tasks_greppable_with_collision_free_ids(self):
        self.call('apply', '--ids', 'todo-done', '--yes')
        todo = (self.repo / 'TODO.md').read_text(encoding='utf-8')
        self.assertIn("grep -n '^- \\[ \\]' TODO.md", todo)
        self.assertIn('not by line', todo)
        self.assertIn('four random hex digits', todo)
        self.assertIn('one line', (self.repo / 'DONE.md').read_text(encoding='utf-8'))

    def test_todo_rules_say_a_task_line_carries_its_context(self):
        self.call('apply', '--ids', 'todo-done', '--yes')
        self.assertIn('no length limit', (self.repo / 'TODO.md').read_text(encoding='utf-8'))

    def test_todo_done_conflict_and_drift_say_how_to_fix_them(self):
        (self.repo / 'TODO.md').write_text('mine\n')
        self.assertIn('one line per task', self.features()['todo-done']['edits'][0]['note'])
        self.assertIn('one line per task', self.call('apply', '--ids', 'todo-done', '--yes')['report'][0]['reason'])
        (self.repo / 'TODO.md').unlink()
        self.call('apply', '--ids', 'todo-done', '--yes')
        todo = self.repo / 'TODO.md'
        todo.write_text(todo.read_text(encoding='utf-8').replace('## Tasks\n', '## Tasks\n\n- [ ] T-1: mine\n'), encoding='utf-8')
        feature = self.features()['todo-done']
        self.assertEqual(feature['state'], 'drift')
        self.assertIn('by hand', feature['edits'][0]['note'])

    def test_multi_line_tasks_are_reported_with_the_fix(self):
        self.call('apply', '--ids', 'todo-done', '--yes')
        self.assertEqual(self.call('status')['warnings'], [])
        todo = self.repo / 'TODO.md'
        todo.write_text(todo.read_text(encoding='utf-8').replace(
            '## Tasks\n', '## Tasks\n\n- [ ] T-1: Title\n  more context on a second line\n- [ ] T-2: fine\n'), encoding='utf-8')
        warnings = self.call('status')['warnings']
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn('TODO.md', warnings[0])
        self.assertIn('one line', warnings[0])

    GUARD_FILES = ('scripts/kaboost_no_verify_guard.py', '.claude/settings.json', '.codex/hooks.json')

    def test_no_verify_guard_installs_agent_hooks_and_removes_them_without_a_trace(self):
        (self.repo / 'README.md').write_bytes(b'# demo\n')
        result = self.call('apply', '--ids', 'no-verify-guard', '--yes')
        self.assertTrue(result['written'], result)
        for name in self.GUARD_FILES:
            self.assertTrue((self.repo / name).is_file(), name)
        claude = json.loads((self.repo / '.claude/settings.json').read_text(encoding='utf-8'))
        handler = claude['hooks']['PreToolUse'][0]['hooks'][0]
        self.assertIn('scripts/kaboost_no_verify_guard.py', handler['command'])
        codex = json.loads((self.repo / '.codex/hooks.json').read_text(encoding='utf-8'))
        self.assertIn('kaboost_no_verify_guard.py', codex['hooks']['PreToolUse'][0]['hooks'][0]['command_windows'])
        self.assertEqual(self.features()['no-verify-guard']['state'], 'enabled')
        self.assertEqual(self.call('apply', '--ids', 'no-verify-guard', '--yes')['changes'], [])
        self.call('disable', '--ids', 'no-verify-guard', '--yes')
        self.assertEqual(sorted(p.name for p in self.repo.rglob('*') if p.is_file()), ['README.md'])

    def test_no_verify_guard_leaves_existing_settings_to_the_user(self):
        settings = self.repo / '.claude/settings.json'
        settings.parent.mkdir()
        settings.write_bytes(b'{"permissions": {}}\n')
        feature = self.features()['no-verify-guard']
        self.assertEqual(feature['state'], 'conflict')
        note = next(e['note'] for e in feature['edits'] if e['target'].endswith('settings.json'))
        self.assertIn('by hand', note)
        self.assertIn('kaboost_no_verify_guard.py', note)
        report = self.call('apply', '--ids', 'no-verify-guard', '--yes')['report'][0]
        self.assertEqual(report['result'], 'skipped')
        self.assertEqual(settings.read_bytes(), b'{"permissions": {}}\n')

    def test_no_verify_guard_settings_edited_after_writing_are_drift(self):
        self.call('apply', '--ids', 'no-verify-guard', '--yes')
        settings = self.repo / '.claude/settings.json'
        edited = settings.read_text(encoding='utf-8').replace('{\n', '{\n  "model": "x",\n', 1)
        settings.write_text(edited, encoding='utf-8')
        self.assertEqual(self.features()['no-verify-guard']['state'], 'drift')
        report = self.call('disable', '--ids', 'no-verify-guard', '--yes')['report'][0]
        self.assertEqual(report['result'], 'skipped')
        self.assertEqual(settings.read_text(encoding='utf-8'), edited)

    def test_tdd_commit_hook_installs_an_executable_hook_and_removes_it_without_a_trace(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        hooks = self.repo / '.git/hooks'
        before = sorted(p.name for p in hooks.iterdir())
        self.call('apply', '--ids', 'tdd-commit-hook', '--yes')
        hook = hooks / 'commit-msg'
        self.assertTrue(hook.read_text(encoding='utf-8').startswith('#!/bin/sh\n# kaboost:begin tdd-commit-hook:hook '))
        if os.name == 'posix':
            self.assertTrue(hook.stat().st_mode & stat.S_IXUSR)
        self.assertTrue((hooks / 'kaboost_tdd_commit_msg.py').is_file())
        self.assertFalse((self.repo / 'scripts').exists())
        self.assertEqual(self.features()['tdd-commit-hook']['state'], 'enabled')
        self.call('disable', '--ids', 'tdd-commit-hook', '--yes')
        self.assertEqual(sorted(p.name for p in hooks.iterdir()), before)

    def test_tdd_commit_hook_leaves_an_existing_commit_msg_hook_alone(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        hook = self.repo / '.git/hooks/commit-msg'
        hook.write_bytes(b'#!/bin/sh\nnpx commitlint --edit "$1"\n')
        self.assertEqual(self.features()['tdd-commit-hook']['state'], 'conflict')
        report = self.call('apply', '--ids', 'tdd-commit-hook', '--yes')['report'][0]
        self.assertEqual(report['result'], 'skipped')
        self.assertEqual(hook.read_bytes(), b'#!/bin/sh\nnpx commitlint --edit "$1"\n')

    def test_tdd_commit_hook_refuses_a_shared_hooks_path(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        shared = self.repo.parent / 'shared-hooks'
        shared.mkdir()
        subprocess.run(['git', '-C', str(self.repo), 'config', 'core.hooksPath', str(shared)], check=True)
        self.assertEqual(self.features()['tdd-commit-hook']['state'], 'conflict')
        self.assertEqual(self.call('apply', '--ids', 'tdd-commit-hook', '--yes')['report'][0]['result'], 'skipped')
        self.assertEqual(list(shared.iterdir()), [])

    def test_tdd_commit_hook_outside_a_git_repository_creates_nothing(self):
        self.assertEqual(self.features()['tdd-commit-hook']['state'], 'conflict')
        report = self.call('apply', '--ids', 'tdd-commit-hook', '--yes')['report'][0]
        self.assertEqual(report['result'], 'skipped')
        self.assertFalse((self.repo / '.git').exists())
        self.assertFalse((self.repo / 'scripts').exists())

    def test_exact_files_written_by_an_older_version_are_outdated(self):
        self.call('apply', '--ids', 'no-verify-guard', '--yes')
        settings = self.repo / '.claude/settings.json'
        old = settings.read_text(encoding='utf-8') + '\n'
        settings.write_text(old, encoding='utf-8')
        catalog = init.load_catalog()
        feature = next(f for f in catalog['features'] if f['id'] == 'no-verify-guard')
        edit = next(e for e in feature['edits'] if e['target'].endswith('settings.json'))
        edit['previous'] = [init.digest(old)]
        with mock.patch.object(init, 'load_catalog', return_value=catalog):
            self.assertEqual(self.features()['no-verify-guard']['state'], 'outdated')
            self.call('apply', '--ids', 'no-verify-guard', '--yes')
            self.assertEqual(self.features()['no-verify-guard']['state'], 'enabled')

    def test_core_and_workflow_leave_tdd_commits_to_the_feature(self):
        for path in ('core/engineering-rules.md', 'workflows/adaptive.md'):
            self.assertNotIn('TDD: red', (ROOT / path).read_text(encoding='utf-8'), path)

    def test_agents_import_already_present_is_not_added_again(self):
        (self.repo / 'CLAUDE.md').write_text('@AGENTS.md\n')
        feature = self.features()['agents-import']
        self.assertEqual(feature['state'], 'enabled')
        self.assertIn('already imports', feature['edits'][0]['note'])
        self.assertEqual(self.call('apply', '--ids', 'agents-import', '--yes')['changes'], [])
        self.assertEqual((self.repo / 'CLAUDE.md').read_text(), '@AGENTS.md\n')

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

    def test_core_reaches_claude_once_through_agents_md(self):
        result = self.call('apply', '--ids', 'core-rules,agents-import', '--yes')
        claude = (self.repo / 'CLAUDE.md').read_text()
        self.assertIn('@AGENTS.md', claude)
        self.assertNotIn('@.claude/kaboost/core-rules.md', claude)
        self.assertFalse((self.repo / '.claude/kaboost/core-rules.md').exists())
        self.assertIn('Engineering rules', (self.repo / 'AGENTS.md').read_text())
        notes = [item.get('note', '') for item in result['report'] if item['feature'] == 'core-rules']
        self.assertIn('AGENTS.md', notes[0])
        self.assertEqual(result['warnings'], [])

    def test_claude_command_skips_its_copy_when_agents_md_has_the_core(self):
        self.call('apply', '--ids', 'core-rules', '--yes', '--targets', 'codex')
        self.call('apply', '--ids', 'agents-import,core-rules', '--yes', '--targets', 'claude')
        self.assertFalse((self.repo / '.claude/kaboost/core-rules.md').exists())
        status = self.call('status', '--targets', 'claude')
        self.assertEqual(status['warnings'], [])
        core = next(f for f in status['features'] if f['id'] == 'core-rules')
        self.assertEqual(core['state'], 'enabled')
        self.assertIn('AGENTS.md', core['edits'][0]['note'])
        self.assertEqual(self.features('repo')['core-rules']['state'], 'enabled')

    def test_existing_duplicate_core_is_reported_with_its_fix(self):
        self.call('apply', '--ids', 'core-rules,agents-import', '--yes', '--targets', 'claude')
        self.assertEqual(self.call('status')['warnings'], [])
        result = self.call('apply', '--ids', 'core-rules', '--yes', '--targets', 'codex')
        self.assertEqual(len(result['warnings']), 1)
        self.assertIn('disable --scope repo --targets claude --ids core-rules', result['warnings'][0])
        self.assertEqual(len(self.call('status')['warnings']), 1)
        self.call('disable', '--ids', 'core-rules', '--yes', '--targets', 'claude')
        self.assertEqual(self.call('status')['warnings'], [])
        self.assertIn('Engineering rules', (self.repo / 'AGENTS.md').read_text())

    def test_init_entry_points_fall_back_from_python3(self):
        order = '`python3`, `python`, `py -3`'
        for name in ('init.md', 'init-global.md'):
            text = (ROOT / 'commands' / name).read_text(encoding='utf-8')
            allowed = next(line for line in text.split('---')[1].splitlines() if line.startswith('allowed-tools:'))
            for launcher in ('python3', 'python', 'py -3'):
                # The pattern must match the quoted command the steps tell the agent to run.
                self.assertIn(f'Bash({launcher} "${{CLAUDE_PLUGIN_ROOT}}/init/kaboost_init.py" *)', allowed)
            self.assertIn(order, text)
            self.assertIn('with the Bash tool exactly as written', text)
            self.assertNotIn('`python3 "', text)
        for name in ('kaboost-init', 'kaboost-init-global'):
            text = (ROOT / 'adapters/codex/skills' / name / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn(order, text)
            self.assertNotIn('`python3 <script>', text)

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
                self.assertIn(edit['mode'], ('own', 'append', 'exact'))
                if edit['mode'] == 'exact':
                    self.assertIn(edit['owner'], init.body_of(edit))
                    self.assertNotIn(init.digest(init.body_of(edit)), edit.get('previous', []))
                if edit.get('frontmatter'):
                    self.assertEqual(edit['mode'], 'own')
                    self.assertTrue(init.parts(edit)[0].startswith('---\n'))
                self.assertTrue(init.body_of(edit).strip())
                self.assertRegex(edit['target'], r'^\{(repo|claude_home|codex_home|git_hooks)\}/')


if __name__ == '__main__':
    unittest.main()

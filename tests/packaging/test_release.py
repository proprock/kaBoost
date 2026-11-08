import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from prepare_release import prepare


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='kaboost release test ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Release fixture')
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')

    def test_reproducible_archives_use_committed_tree(self):
        first, second = self.base / 'first', self.base / 'second'
        sha = prepare(self.root, 'HEAD', first)
        (self.root / 'CHANGELOG.md').write_text('uncommitted change', encoding='utf-8')
        self.assertEqual(prepare(self.root, 'HEAD', second), sha)
        for path in first.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
        metadata = json.loads((first / 'release.json').read_text())
        self.assertEqual(metadata['source_commit'], sha)
        self.assertEqual(metadata['status'], 'local-unpublished')
        for name in metadata['artifacts_sha256']:
            with zipfile.ZipFile(first / name) as bundle:
                self.assertTrue(any(path.endswith('SHA256SUMS.json') for path in bundle.namelist()))
                self.assertTrue(any(path.endswith('marketplace.json') for path in bundle.namelist()))

    def test_archive_bytes_do_not_depend_on_the_platform_or_zlib(self):
        # A Windows build had the same files as Linux but other bytes: create_system defaulted to fat, and zlib-ng
        # deflated differently. Unix as the system and stored entries leave no platform input (KB-316).
        out = self.base / 'out'
        prepare(self.root, 'HEAD', out)
        for name in json.loads((out / 'release.json').read_text())['artifacts_sha256']:
            with zipfile.ZipFile(out / name) as bundle:
                for info in bundle.infolist():
                    with self.subTest(archive=name, entry=info.filename):
                        self.assertEqual(info.create_system, 3)
                        self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                        self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))

    def test_rejects_inconsistent_committed_changelog(self):
        (self.root / 'CHANGELOG.md').write_text('# Changelog\n', encoding='utf-8')
        self.commit()
        with self.assertRaisesRegex(ValueError, 'Changelog'):
            prepare(self.root, 'HEAD', self.base / 'out')
        self.assertFalse((self.base / 'out').exists())

    def test_rejects_existing_output(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            prepare(self.root, 'HEAD', self.base)

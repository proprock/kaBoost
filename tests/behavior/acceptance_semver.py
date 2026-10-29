"""Independent medium-pilot check; run against an isolated candidate checkout.

Usage: python3 acceptance_semver.py /path/to/candidate-checkout
This file must stay outside the checkout presented to an agent during a trial.
"""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


CHECKOUT = Path(sys.argv.pop(1)).resolve()
sys.path.insert(0, str(CHECKOUT / 'scripts'))
from build import build
from validate import validate


class StableVersionAcceptance(unittest.TestCase):
    def check_version(self, version, valid):
        with tempfile.TemporaryDirectory(prefix='kaboost-pilot-acceptance-') as temp:
            root = Path(temp) / 'checkout'
            shutil.copytree(CHECKOUT, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
            for name in ('toolkit.json', 'adapters/claude-code/plugin.json', '.claude-plugin/marketplace.json'):
                path = root / name
                data = json.loads(path.read_text(encoding='utf-8'))
                if 'plugins' in data:
                    data['plugins'][0]['version'] = version
                else:
                    data['version'] = version
                path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
            build(root)
            if valid:
                validate(root)
            else:
                with self.assertRaises(ValueError):
                    validate(root)

    def test_valid_stable_versions(self):
        for version in ('0.0.0', '1.2.3', '10.20.30'):
            with self.subTest(version=version):
                self.check_version(version, True)

    def test_invalid_stable_versions(self):
        for version in ('01.2.3', '1.02.3', '1.2.03', '١.2.3', '1.2.3-rc.1', '1.2.3+build'):
            with self.subTest(version=version):
                self.check_version(version, False)


if __name__ == '__main__':
    unittest.main()

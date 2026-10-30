import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_plugin_eval as runner  # noqa: E402


class PluginEvalSetupTests(unittest.TestCase):
    def test_assemble_fills_fixture_and_leaves_sources_alone(self):
        original = (runner.ROOT / 'evals' / 'large-json-cli' / 'fixture.sh').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory() as temp:
            plugin = runner.assemble(Path(temp).resolve())
            fixture = (plugin / 'evals' / 'large-json-cli' / 'fixture.sh').read_text(encoding='utf-8')
            self.assertTrue((plugin / 'skills' / 'plan-before-edit' / 'SKILL.md').is_file())
        self.assertNotIn('@SOURCE@', fixture)
        self.assertIn(runner.pilot.COMMIT, fixture)
        self.assertIn('@SOURCE@', original)
        self.assertFalse((runner.ROOT / 'plugins' / 'kaboost' / 'evals').exists())

    def test_estimate_counts_both_arms(self):
        self.assertEqual(runner.estimate(runner.ROOT / 'evals', 1), round(runner.PER_RUN_USD * 2 * len(runner.cases(runner.ROOT / 'evals')), 2))

    def test_ordering_grader_is_not_scored_without_plugin(self):
        text = (runner.ROOT / 'evals' / 'large-json-cli' / 'graders' / 'skill-before-edit.md').read_text(encoding='utf-8')
        self.assertIn('arm: with-only', text)


if __name__ == '__main__':
    unittest.main()

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import measure_context as mc  # noqa: E402


class MeasureContextTests(unittest.TestCase):
    def test_tokens_round_up_from_characters(self):
        self.assertEqual((mc.tokens(''), mc.tokens('abcd'), mc.tokens('abcde')), (0, 1, 2))

    def test_front_matter_is_split_from_body(self):
        fields, body = mc.front_matter('---\nname: x\ndescription: d: e\n---\nBody')
        self.assertEqual((fields, body), ({'name': 'x', 'description': 'd: e'}, 'Body'))

    def test_front_matter_is_required(self):
        with self.assertRaises(ValueError):
            mc.front_matter('no front matter')

    def test_shipped_content_is_within_budgets(self):
        result = mc.measure()
        self.assertEqual(mc.violations(result), [])
        self.assertEqual(result['always'], result['core'] + result['listing'])

    def test_violations_name_the_exceeded_tier(self):
        result = {'always': mc.BUDGETS['always'] + 1, 'skill_body_max': 0, 'command_body_max': 0}
        self.assertEqual(len(mc.violations(result)), 1)
        self.assertIn('always', mc.violations(result)[0])


if __name__ == '__main__':
    unittest.main()

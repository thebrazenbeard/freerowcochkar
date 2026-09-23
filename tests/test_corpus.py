import json
import unittest
from pathlib import Path

from freerowcochkar import analyze


FIXTURE = Path(__file__).parent / "fixtures" / "v1_cases.json"


class CorpusTests(unittest.TestCase):
    def test_v1_adversarial_corpus(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schema_version"])

        for case in payload["cases"]:
            with self.subTest(case=case["id"]):
                report = analyze(case["text"], profile=case["profile"])
                categories = {finding.category for finding in report.findings}
                for category in case["must_include"]:
                    self.assertIn(category, categories)
                for category in case["must_exclude"]:
                    self.assertNotIn(category, categories)


if __name__ == "__main__":
    unittest.main()

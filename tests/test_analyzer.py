import unittest

from freerowcochkar import analyze


class AnalyzerTests(unittest.TestCase):
    def test_flags_vague_normative_language(self):
        report = analyze("The operator must take reasonable steps before release.")
        self.assertIn("ambiguous_scope", {f.category for f in report.findings})

    def test_flags_conflicting_overlapping_rules(self):
        text = """
        Operators must not export customer records.
        Operators may export customer records for support.
        """
        report = analyze(text)
        self.assertIn("precedence_collision", {f.category for f in report.findings})

    def test_flags_required_dependency_without_failure_rule(self):
        text = "The reviewer must consult the external database before approval."
        report = analyze(text)
        self.assertIn("failure_mode_gap", {f.category for f in report.findings})

    def test_failure_language_suppresses_dependency_gap(self):
        text = """
        The reviewer must consult the external database before approval.
        If the database is unavailable, approval must stop and status is UNKNOWN.
        """
        report = analyze(text)
        self.assertNotIn("failure_mode_gap", {f.category for f in report.findings})

    def test_unrelated_error_word_does_not_hide_dependency_gap(self):
        text = """
        Errors in optional reporting should be logged.
        The reviewer must consult the external database before approval.
        This appendix explains unrelated formatting.
        This appendix explains unrelated formatting.
        This appendix explains unrelated formatting.
        This appendix explains unrelated formatting.
        """
        report = analyze(text)
        self.assertIn("failure_mode_gap", {f.category for f in report.findings})

    def test_flags_indirect_effect_gap(self):
        report = analyze("Operators must not delete protected records.")
        self.assertIn("indirect_effect_gap", {f.category for f in report.findings})

    def test_explicit_indirect_scope_closes_indirect_effect_gap(self):
        report = analyze(
            "Operators must not directly or indirectly delete protected records "
            "or cause another actor to delete them."
        )
        self.assertNotIn("indirect_effect_gap", {f.category for f in report.findings})

    def test_code_profile_flags_swallowed_exception(self):
        text = """
def authorized():
    try:
        return check_policy()
    except Exception:
        pass
        """
        report = analyze(text, profile="code")
        self.assertIn("silent_failure", {f.category for f in report.findings})

    def test_json_shape_is_stable(self):
        report = analyze("Operators must take appropriate action.", intent="deny unsafe effects")
        payload = report.to_dict()
        self.assertEqual("instructions", payload["profile"])
        self.assertEqual("deny unsafe effects", payload["intent"])
        self.assertGreaterEqual(payload["finding_count"], 1)
        self.assertIn("risk_score", payload)


if __name__ == "__main__":
    unittest.main()

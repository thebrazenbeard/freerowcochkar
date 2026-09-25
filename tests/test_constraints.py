import unittest

from freerowcochkar.constraints import ConstraintGraph, Modality
from freerowcochkar.rules import extract_rules, extract_state_model


class ConstraintGraphTests(unittest.TestCase):
    def test_extracts_typed_rules(self):
        rules = extract_rules(
            "Operators must not delete protected records.\n"
            "Supervisors may export audit records."
        )
        self.assertEqual(2, len(rules))
        self.assertEqual(Modality.PROHIBIT, rules[0].modality)
        self.assertEqual("delete", rules[0].action)
        self.assertEqual("protected records", rules[0].object)
        self.assertEqual("delete:protected records", rules[0].effect_key)
        self.assertEqual(Modality.PERMIT, rules[1].modality)

    def test_detects_delegation_laundering_across_separate_rules(self):
        rules = extract_rules(
            "Operators must not delete protected records.\n"
            "Operators may instruct the cleanup service to delete protected records."
        )
        graph = ConstraintGraph.from_rules(rules)
        paths = graph.search_literal_compliance_paths()
        self.assertIn("delegation_laundering", {p.category for p in paths})

    def test_direct_and_indirect_ban_closes_delegation_path(self):
        rules = extract_rules(
            "Operators must not directly or indirectly delete protected records.\n"
            "Operators may instruct the cleanup service to delete protected records."
        )
        self.assertTrue(rules[0].indirect)
        graph = ConstraintGraph.from_rules(rules)
        categories = {p.category for p in graph.search_literal_compliance_paths()}
        self.assertNotIn("delegation_laundering", categories)

    def test_graph_snapshot_preserves_source_and_paths(self):
        rules = extract_rules(
            "Operators must not delete protected records.\n"
            "Operators may instruct the cleanup service to delete protected records."
        )
        payload = ConstraintGraph.from_rules(rules).to_dict()
        self.assertIn("effect:delete:protected records", payload["nodes"])
        self.assertEqual("protected records", payload["rules"][0]["object"])
        self.assertEqual("delegation_laundering", payload["paths"][0]["category"])

    def test_scope_qualifiers_do_not_collapse_into_false_conflict(self):
        rules = extract_rules(
            "Operators must not export customer records.\n"
            "Operators may export audit records."
        )
        graph = ConstraintGraph.from_rules(rules)
        self.assertEqual([], graph.search_literal_compliance_paths())

    def test_detects_same_effect_permission_conflict(self):
        rules = extract_rules(
            "Operators must not export customer records.\n"
            "Operators may export customer records."
        )
        graph = ConstraintGraph.from_rules(rules)
        self.assertIn(
            "literal_permission_conflict",
            {p.category for p in graph.search_literal_compliance_paths()},
        )


    def test_extracts_state_transition_model(self):
        text = (
            "Operators may transition release from draft to reviewed.\n"
            "Operators must not transition release from approved to deployed.\n"
            "The release state deployed is prohibited."
        )
        transitions, forbidden_states = extract_state_model(text)
        self.assertEqual(2, len(transitions))
        self.assertEqual(Modality.PERMIT, transitions[0].modality)
        self.assertEqual(Modality.PROHIBIT, transitions[1].modality)
        self.assertEqual(
            ("release", "draft", "reviewed"),
            (
                transitions[0].resource,
                transitions[0].from_state,
                transitions[0].to_state,
            ),
        )
        self.assertEqual(1, len(forbidden_states))
        self.assertEqual("deployed", forbidden_states[0].state)

    def test_three_step_composition_reaches_forbidden_state(self):
        text = (
            "Operators may transition release from draft to reviewed.\n"
            "Operators may transition release from reviewed to approved.\n"
            "Operators may transition release from approved to deployed.\n"
            "The release state deployed is prohibited."
        )
        transitions, forbidden_states = extract_state_model(text)
        graph = ConstraintGraph.from_rules(
            extract_rules(text),
            transitions=transitions,
            forbidden_states=forbidden_states,
        )
        composition = [
            path
            for path in graph.search_literal_compliance_paths()
            if path.category == "composition_gap"
        ]
        self.assertEqual(1, len(composition))
        self.assertEqual(
            ("T0001", "T0002", "T0003", "S0001"),
            composition[0].rule_ids,
        )

    def test_two_step_path_does_not_trigger_composition(self):
        text = (
            "Operators may transition release from draft to approved.\n"
            "Operators may transition release from approved to deployed.\n"
            "The release state deployed is prohibited."
        )
        transitions, forbidden_states = extract_state_model(text)
        graph = ConstraintGraph.from_rules(
            extract_rules(text),
            transitions=transitions,
            forbidden_states=forbidden_states,
        )
        categories = {
            path.category for path in graph.search_literal_compliance_paths()
        }
        self.assertNotIn("composition_gap", categories)

    def test_transition_prohibition_rewrite_closes_composition_path(self):
        text = (
            "Operators may transition release from draft to reviewed.\n"
            "Operators may transition release from reviewed to approved.\n"
            "Operators must not transition release from approved to deployed.\n"
            "The release state deployed is prohibited."
        )
        transitions, forbidden_states = extract_state_model(text)
        graph = ConstraintGraph.from_rules(
            extract_rules(text),
            transitions=transitions,
            forbidden_states=forbidden_states,
        )
        categories = {
            path.category for path in graph.search_literal_compliance_paths()
        }
        self.assertNotIn("composition_gap", categories)

    def test_cycle_does_not_create_unbounded_composition(self):
        text = (
            "Operators may transition release from draft to reviewed.\n"
            "Operators may transition release from reviewed to draft.\n"
            "The release state deployed is prohibited."
        )
        transitions, forbidden_states = extract_state_model(text)
        graph = ConstraintGraph.from_rules(
            extract_rules(text),
            transitions=transitions,
            forbidden_states=forbidden_states,
        )
        composition = [
            path
            for path in graph.search_literal_compliance_paths(
                max_transition_depth=32
            )
            if path.category == "composition_gap"
        ]
        self.assertEqual([], composition)


if __name__ == "__main__":
    unittest.main()

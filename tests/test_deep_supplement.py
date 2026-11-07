"""Supplementary Level 3 set: numeric strings and multi-defect records.

The labels in level-3-deep/supplement.json were committed before
run_supplement.py existed. These tests pin that every record ends
in its labelled status and that the committed results reproduce.
Run: python -m unittest discover -s tests -p "test_deep*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from run_supplement import evaluate  # noqa: E402


class SupplementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = evaluate()
        cls.rows = {r["id"]: r for r in cls.results["per_record"]}

    def test_every_record_matches_its_label(self):
        self.assertEqual(self.results["summary"]["matched"], self.results["summary"]["attempted"])

    def test_coercion_rule_is_exercised(self):
        self.assertGreater(self.results["summary"]["coerce_repairs_applied"], 0)

    def test_fractional_string_never_becomes_an_integer(self):
        row = self.rows["r03-product-stock-fractional-string"]
        self.assertEqual(row["status"], "still_rejected")
        self.assertEqual(row["final_record"]["stock"], "4.5")

    def test_unrepairable_defect_keeps_record_rejected_with_full_log(self):
        row = self.rows["r07-invoice-extra-field-and-missing-vendor"]
        self.assertEqual(row["status"], "still_rejected")
        rules = [e["rule"] for e in row["repair_log"]]
        self.assertIn("drop_additional_field", rules)
        self.assertIn("none_unrepairable", rules)
        self.assertNotIn("vendor", row["final_record"])

    def test_coerce_then_clamp_is_flagged_and_silent(self):
        row = self.rows["r10-invoice-total-string-out-of-range"]
        self.assertEqual(row["status"], "healed_flagged")
        self.assertTrue(row["silent_failure"])
        self.assertEqual([e["rule"] for e in row["repair_log"]], ["coerce_numeric_string", "clamp_to_range"])

    def test_committed_results_reproduce(self):
        with open(os.path.join(ROOT, "level-3-deep", "results_supplement.json"), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), json.loads(json.dumps(self.results)))


if __name__ == "__main__":
    unittest.main()

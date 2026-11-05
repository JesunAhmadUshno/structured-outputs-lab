"""Level 3 Deep tests. Every expected outcome below was worked
out by hand from DEEP-SPEC.md, the Level 2 schemas, and the
labelled set in level-3-deep/evaluation_deep.json before the
code ran.
Run: python -m unittest discover -s tests -p "test_deep*.py" -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from corpus import DOCUMENTS  # noqa: E402
from pipeline import INVOICE_SCHEMA, SCHEMAS, run_pipeline  # noqa: E402
from heal import (  # noqa: E402
    MAX_ROUNDS,
    RULE_CLAMP,
    RULE_COERCE_NUMERIC,
    RULE_DROP_ADDITIONAL,
    RULE_NONE,
    attempt_heal,
    heal_rejected,
)
from run_deep import evaluate  # noqa: E402


def rejected_by_id():
    _, rejected = run_pipeline(DOCUMENTS)
    return {o["id"]: o for o in rejected}


def accepted_outcomes():
    accepted, _ = run_pipeline(DOCUMENTS)
    return accepted


def valid_invoice(**overrides):
    record = {
        "invoice_id": "INV-1001",
        "vendor": "Northlight Supplies",
        "date": "2026-10-02",
        "total_cad": 249.5,
        "items_count": 4,
    }
    record.update(overrides)
    return record


class TestSafeRepairs(unittest.TestCase):
    def test_drop_additional_field_heals_d11_exactly(self):
        outcome = rejected_by_id()["d11-invoice-extra-field"]
        result = heal_rejected(outcome)
        self.assertTrue(result["healed"])
        self.assertEqual(result["status"], "healed_clean")
        self.assertFalse(result["flagged"])
        self.assertEqual(
            result["record"],
            {
                "invoice_id": "INV-1006",
                "vendor": "Paper Trail Office Co",
                "date": "2026-10-13",
                "total_cad": 75.25,
                "items_count": 2,
            },
        )
        self.assertEqual(result["repair_log"][0]["rule"], RULE_DROP_ADDITIONAL)
        self.assertEqual(result["repair_log"][0]["before"], 5.0)

    def test_coerce_numeric_string_to_number(self):
        record = valid_invoice(total_cad="249.50")
        result = attempt_heal(record, INVOICE_SCHEMA, doc_id="t-num")
        self.assertTrue(result["healed"])
        self.assertEqual(result["record"]["total_cad"], 249.5)
        self.assertEqual(result["repair_log"][0]["rule"], RULE_COERCE_NUMERIC)
        self.assertFalse(result["repair_log"][0]["value_changing"])

    def test_coerce_numeric_string_to_integer(self):
        record = valid_invoice(items_count="4")
        result = attempt_heal(record, INVOICE_SCHEMA, doc_id="t-int")
        self.assertTrue(result["healed"])
        self.assertEqual(result["record"]["items_count"], 4)
        self.assertIsInstance(result["record"]["items_count"], int)

    def test_float_string_never_becomes_integer(self):
        record = valid_invoice(items_count="4.5")
        result = attempt_heal(record, INVOICE_SCHEMA, doc_id="t-floatint")
        self.assertFalse(result["healed"])
        self.assertEqual(result["status"], "still_rejected")
        self.assertEqual(result["record"]["items_count"], "4.5")

    def test_non_numeric_string_stays_rejected(self):
        outcome = rejected_by_id()["d10-invoice-bad-total-type"]
        result = heal_rejected(outcome)
        self.assertFalse(result["healed"])
        self.assertEqual(result["record"]["total_cad"], "FREE")
        self.assertEqual(result["repair_log"][0]["rule"], RULE_NONE)
        self.assertEqual(result["repair_log"][0]["outcome"], "unrepairable")

    def test_boolean_is_never_coerced_to_number(self):
        record = valid_invoice(total_cad=True)
        result = attempt_heal(record, INVOICE_SCHEMA, doc_id="t-bool")
        self.assertFalse(result["healed"])
        self.assertIs(result["record"]["total_cad"], True)


class TestUnrepairable(unittest.TestCase):
    def test_missing_vendor_stays_rejected_and_is_not_invented(self):
        outcome = rejected_by_id()["d09-invoice-missing-vendor"]
        result = heal_rejected(outcome)
        self.assertFalse(result["healed"])
        self.assertNotIn("vendor", result["record"])
        self.assertEqual(result["repair_log"][0]["code"], "required")
        self.assertEqual(result["repair_log"][0]["outcome"], "unrepairable")

    def test_missing_title_stays_rejected(self):
        outcome = rejected_by_id()["d13-meeting-missing-title"]
        result = heal_rejected(outcome)
        self.assertFalse(result["healed"])
        self.assertNotIn("title", result["record"])

    def test_bad_enum_stays_rejected_and_is_not_mapped(self):
        outcome = rejected_by_id()["d16-product-bad-category"]
        result = heal_rejected(outcome)
        self.assertFalse(result["healed"])
        self.assertEqual(result["record"]["category"], "toys")
        self.assertEqual(result["repair_log"][0]["code"], "enum")

    def test_non_numeric_stock_stays_rejected(self):
        outcome = rejected_by_id()["d15-product-bad-stock-type"]
        result = heal_rejected(outcome)
        self.assertFalse(result["healed"])
        self.assertEqual(result["record"]["stock"], "many")


class TestClampFlagging(unittest.TestCase):
    def test_clamp_total_heals_flagged_at_the_bound(self):
        outcome = rejected_by_id()["d12-invoice-total-out-of-range"]
        result = heal_rejected(outcome)
        self.assertTrue(result["healed"])
        self.assertEqual(result["status"], "healed_flagged")
        self.assertTrue(result["flagged"])
        self.assertEqual(result["record"]["total_cad"], 100000)
        entry = result["repair_log"][0]
        self.assertEqual(entry["rule"], RULE_CLAMP)
        self.assertTrue(entry["value_changing"])
        self.assertEqual(entry["before"], 250000.0)
        self.assertEqual(entry["after"], 100000)
        self.assertEqual(entry["outcome"], "applied_value_changing")

    def test_clamp_duration_heals_flagged_at_the_bound(self):
        outcome = rejected_by_id()["d14-meeting-duration-out-of-range"]
        result = heal_rejected(outcome)
        self.assertTrue(result["healed"])
        self.assertEqual(result["record"]["duration_minutes"], 480)
        self.assertTrue(result["flagged"])


class TestLogAndLoopGuarantees(unittest.TestCase):
    def test_every_repair_attempt_is_logged_for_all_rejected(self):
        for doc_id, outcome in rejected_by_id().items():
            result = heal_rejected(outcome)
            self.assertTrue(result["repair_log"], doc_id)
            for entry in result["repair_log"]:
                for field in (
                    "doc_id", "round", "path", "code", "rule",
                    "before", "after", "value_changing", "outcome",
                ):
                    self.assertIn(field, entry, doc_id)
                self.assertEqual(entry["doc_id"], doc_id)

    def test_healed_record_always_carries_a_log(self):
        for outcome in rejected_by_id().values():
            result = heal_rejected(outcome)
            if result["healed"]:
                self.assertTrue(result["repair_log"], result["id"])
                self.assertEqual(result["errors"], [])

    def test_loop_is_bounded_at_max_rounds(self):
        for outcome in rejected_by_id().values():
            result = heal_rejected(outcome)
            self.assertLessEqual(result["rounds"], MAX_ROUNDS)

    def test_two_round_repair_and_bound_enforcement(self):
        # String "900" for duration: round 1 coerces to the integer
        # 900, round 2 clamps it to 480. With max_rounds 1 the same
        # record must not heal, proving the bound is real.
        record = {
            "meeting_id": "MTG-2005",
            "title": "All Hands",
            "date": "2026-10-16",
            "attendees": ["Ana", "Ben", "Cara"],
            "duration_minutes": "900",
        }
        schema = SCHEMAS["meeting_note"]
        healed = attempt_heal(record, schema, doc_id="t-two-round")
        self.assertTrue(healed["healed"])
        self.assertEqual(healed["record"]["duration_minutes"], 480)
        self.assertTrue(healed["flagged"])
        bounded = attempt_heal(record, schema, doc_id="t-two-round", max_rounds=1)
        self.assertFalse(bounded["healed"])
        self.assertLessEqual(bounded["rounds"], 1)

    def test_input_record_is_never_mutated(self):
        outcome = rejected_by_id()["d11-invoice-extra-field"]
        original = dict(outcome["record"])
        heal_rejected(outcome)
        self.assertEqual(outcome["record"], original)
        self.assertIn("discount", outcome["record"])

    def test_no_valid_record_is_altered(self):
        for outcome in accepted_outcomes():
            result = heal_rejected(outcome)
            self.assertEqual(result["status"], "already_valid", outcome["id"])
            self.assertEqual(result["record"], outcome["record"], outcome["id"])
            self.assertEqual(result["repair_log"], [])


class TestBenchmarkNumbers(unittest.TestCase):
    def test_summary_matches_labelled_expectations(self):
        results = evaluate()
        summary = results["summary"]
        self.assertEqual(summary["attempted"], 8)
        self.assertEqual(summary["healed"], 3)
        self.assertEqual(summary["healed_clean"], 1)
        self.assertEqual(summary["healed_flagged"], 2)
        self.assertEqual(summary["still_rejected"], 5)
        self.assertEqual(summary["repair_rate"], 0.375)
        self.assertEqual(summary["silent_failures"], 2)
        self.assertEqual(summary["silent_failure_rate"], 0.667)
        self.assertEqual(summary["valid_records_altered"], 0)
        self.assertEqual(summary["matched"], 8)

    def test_per_defect_class_outcomes(self):
        per_class = evaluate()["per_defect_class"]
        self.assertEqual(per_class["missing"], {"attempted": 2, "healed": 0, "healed_flagged": 0, "silent_failures": 0})
        self.assertEqual(per_class["wrong_type"], {"attempted": 2, "healed": 0, "healed_flagged": 0, "silent_failures": 0})
        self.assertEqual(per_class["extra_field"], {"attempted": 1, "healed": 1, "healed_flagged": 0, "silent_failures": 0})
        self.assertEqual(per_class["out_of_range"], {"attempted": 2, "healed": 2, "healed_flagged": 2, "silent_failures": 2})
        self.assertEqual(per_class["bad_enum"], {"attempted": 1, "healed": 0, "healed_flagged": 0, "silent_failures": 0})

    def test_evaluate_is_deterministic(self):
        self.assertEqual(evaluate(), evaluate())


if __name__ == "__main__":
    unittest.main()

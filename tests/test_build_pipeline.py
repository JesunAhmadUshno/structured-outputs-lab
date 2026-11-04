"""Level 2 Build tests. Every expected record and error path below
was worked out by hand from the corpus texts and the schemas in
level-2-build/pipeline.py before the code ran.
Run: python -m unittest discover -s tests -p "test_build*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from corpus import DOCUMENTS  # noqa: E402
from pipeline import (  # noqa: E402
    INVOICE_SCHEMA,
    SCHEMAS,
    extract_and_validate,
    extract_invoice,
    extract_meeting,
    extract_product,
    run_pipeline,
)
from schema_validate import validate  # noqa: E402


def by_id(doc_id):
    return next(d for d in DOCUMENTS if d["id"] == doc_id)


class TestExtractors(unittest.TestCase):
    def test_invoice_extractor_exact_record(self):
        record = extract_invoice(by_id("d01-invoice-valid")["text"])
        self.assertEqual(
            record,
            {
                "invoice_id": "INV-1001",
                "vendor": "Northlight Supplies",
                "date": "2026-10-02",
                "total_cad": 249.5,
                "items_count": 4,
            },
        )

    def test_meeting_extractor_exact_record(self):
        record = extract_meeting(by_id("d03-meeting-valid")["text"])
        self.assertEqual(
            record,
            {
                "meeting_id": "MTG-2001",
                "title": "Sprint Planning",
                "date": "2026-10-03",
                "attendees": ["Ana", "Ben", "Cara"],
                "duration_minutes": 60,
            },
        )

    def test_product_extractor_exact_record(self):
        record = extract_product(by_id("d05-product-valid")["text"])
        self.assertEqual(
            record,
            {
                "sku": "SKU-3001",
                "name": "Steel Hammer",
                "price_cad": 24.99,
                "stock": 140,
                "category": "tools",
            },
        )

    def test_non_numeric_total_stays_a_string(self):
        record = extract_invoice(by_id("d10-invoice-bad-total-type")["text"])
        self.assertEqual(record["total_cad"], "FREE")
        self.assertIsInstance(record["total_cad"], str)

    def test_missing_line_means_missing_field(self):
        record = extract_invoice(by_id("d09-invoice-missing-vendor")["text"])
        self.assertNotIn("vendor", record)

    def test_extra_line_becomes_extra_field(self):
        record = extract_invoice(by_id("d11-invoice-extra-field")["text"])
        self.assertEqual(record["discount"], 5.0)


class TestSchemas(unittest.TestCase):
    def test_all_three_types_have_strict_schemas(self):
        self.assertEqual(sorted(SCHEMAS), ["invoice", "meeting_note", "product_listing"])
        for schema in SCHEMAS.values():
            self.assertIs(schema["additionalProperties"], False)
            self.assertEqual(sorted(schema["required"]), sorted(schema["properties"]))

    def test_valid_invoice_record_passes(self):
        record = extract_invoice(by_id("d02-invoice-valid")["text"])
        self.assertEqual(validate(record, INVOICE_SCHEMA), [])

    def test_out_of_range_total_error_path_and_code(self):
        record = extract_invoice(by_id("d12-invoice-total-out-of-range")["text"])
        errors = validate(record, INVOICE_SCHEMA)
        self.assertEqual(errors[0]["path"], "$.total_cad")
        self.assertEqual(errors[0]["code"], "maximum")

    def test_bad_category_is_enum_error(self):
        outcome = extract_and_validate(by_id("d16-product-bad-category"))
        self.assertEqual(outcome["errors"][0]["path"], "$.category")
        self.assertEqual(outcome["errors"][0]["code"], "enum")


class TestPipelineRouting(unittest.TestCase):
    def test_valid_documents_are_accepted(self):
        for doc_id in ("d01-invoice-valid", "d05-product-valid", "d08-meeting-valid"):
            outcome = extract_and_validate(by_id(doc_id))
            self.assertTrue(outcome["accepted"], doc_id)
            self.assertEqual(outcome["errors"], [])

    def test_each_malformed_document_rejected_at_designed_path(self):
        expected = {
            "d09-invoice-missing-vendor": "$.vendor",
            "d10-invoice-bad-total-type": "$.total_cad",
            "d11-invoice-extra-field": "$.discount",
            "d12-invoice-total-out-of-range": "$.total_cad",
            "d13-meeting-missing-title": "$.title",
            "d14-meeting-duration-out-of-range": "$.duration_minutes",
            "d15-product-bad-stock-type": "$.stock",
            "d16-product-bad-category": "$.category",
        }
        for doc_id, path in expected.items():
            outcome = extract_and_validate(by_id(doc_id))
            self.assertFalse(outcome["accepted"], doc_id)
            self.assertEqual(outcome["errors"][0]["path"], path, doc_id)

    def test_rejection_error_codes(self):
        cases = {
            "d09-invoice-missing-vendor": "required",
            "d10-invoice-bad-total-type": "type",
            "d11-invoice-extra-field": "additional",
            "d14-meeting-duration-out-of-range": "maximum",
            "d15-product-bad-stock-type": "type",
        }
        for doc_id, code in cases.items():
            outcome = extract_and_validate(by_id(doc_id))
            self.assertEqual(outcome["errors"][0]["code"], code, doc_id)

    def test_full_pipeline_split_is_8_and_8(self):
        accepted, rejected = run_pipeline(DOCUMENTS)
        self.assertEqual(len(accepted), 8)
        self.assertEqual(len(rejected), 8)
        accepted_ids = {o["id"] for o in accepted}
        rejected_ids = {o["id"] for o in rejected}
        self.assertFalse(accepted_ids & rejected_ids)
        self.assertEqual(len(accepted_ids | rejected_ids), 16)

    def test_no_rejected_record_is_in_accepted_list(self):
        accepted, rejected = run_pipeline(DOCUMENTS)
        for outcome in rejected:
            self.assertTrue(outcome["errors"])
        for outcome in accepted:
            self.assertEqual(outcome["errors"], [])

    def test_unknown_type_is_structured_rejection(self):
        outcome = extract_and_validate(
            {"id": "x1", "doc_type": "memo", "text": "Memo\nBody: hi\n"}
        )
        self.assertFalse(outcome["accepted"])
        self.assertEqual(outcome["errors"][0]["code"], "unknown_type")
        self.assertEqual(outcome["errors"][0]["path"], "$")
        self.assertIsNone(outcome["record"])

    def test_corpus_shape(self):
        self.assertEqual(len(DOCUMENTS), 16)
        self.assertEqual(
            sorted({d["doc_type"] for d in DOCUMENTS}),
            ["invoice", "meeting_note", "product_listing"],
        )
        ids = [d["id"] for d in DOCUMENTS]
        self.assertEqual(len(ids), len(set(ids)))


class TestEvaluationSet(unittest.TestCase):
    def test_evaluation_matches_corpus_and_outcomes(self):
        path = os.path.join(ROOT, "level-2-build", "evaluation.json")
        with open(path, encoding="utf-8") as fh:
            evaluation = json.load(fh)
        self.assertEqual(len(evaluation), 16)
        by_eval = {entry["id"]: entry for entry in evaluation}
        for document in DOCUMENTS:
            entry = by_eval[document["id"]]
            outcome = extract_and_validate(document)
            self.assertEqual(outcome["accepted"], entry["expect_ok"], document["id"])
            if entry["expect_ok"]:
                for field, value in entry["expected_fields"].items():
                    self.assertEqual(outcome["record"][field], value, document["id"])
            else:
                self.assertEqual(
                    outcome["errors"][0]["path"],
                    entry["expect_first_path"],
                    document["id"],
                )


if __name__ == "__main__":
    unittest.main()

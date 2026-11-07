"""Differential check: the Level 1 subset validator against jsonschema.

The subset validator is hand written. This test asks a widely used
reference implementation (the jsonschema package, Draft 2020-12)
the same accept or reject question for every input the repo
measures: the 9 parseable Level 1 case arguments and the 16 Level 2
candidate records. They must agree on every one. One known,
deliberate disagreement is pinned as its own test so it stays
visible: the subset follows Python types and rejects 60.0 for an
integer field, while Draft 2020-12 counts 60.0 as an integer.

jsonschema is a test-only dependency (CI installs it). Without it
the tests skip; the stdlib-only runtime is unchanged.
Run: python -m unittest discover -s tests -p "test_learn*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

from corpus import DOCUMENTS  # noqa: E402
from function_calling import build_default_registry  # noqa: E402
from pipeline import EXTRACTORS, SCHEMAS  # noqa: E402
from schema_validate import validate  # noqa: E402

try:
    import jsonschema
except ImportError:  # pragma: no cover - exercised only where jsonschema is absent
    jsonschema = None


def reference_ok(value, schema):
    return jsonschema.Draft202012Validator(schema).is_valid(value)


@unittest.skipIf(jsonschema is None, "jsonschema not installed")
class DifferentialTests(unittest.TestCase):
    def test_level1_cases_agree(self):
        registry = build_default_registry()
        with open(os.path.join(ROOT, "level-1-learn", "cases.json"), encoding="utf-8") as fh:
            cases = json.load(fh)
        checked = 0
        for case in cases:
            args = case["arguments"]
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    continue  # invalid JSON never reaches a validator
            schema = registry.schema_for(case["function"])
            with self.subTest(case=case["id"]):
                self.assertEqual(not validate(args, schema), reference_ok(args, schema))
            checked += 1
        self.assertEqual(checked, 9)

    def test_level2_records_agree(self):
        for document in DOCUMENTS:
            schema = SCHEMAS[document["doc_type"]]
            record = EXTRACTORS[document["doc_type"]](document["text"])
            with self.subTest(doc=document["id"]):
                self.assertEqual(not validate(record, schema), reference_ok(record, schema))

    def test_known_disagreement_integral_float(self):
        schema = {"type": "integer"}
        self.assertTrue(validate(60.0, schema))  # subset: float is not an integer
        self.assertTrue(reference_ok(60.0, schema))  # Draft 2020-12: 60.0 is an integer

    def test_bool_is_never_a_number_in_either(self):
        for schema in ({"type": "integer"}, {"type": "number"}):
            self.assertTrue(validate(True, schema))
            self.assertFalse(reference_ok(True, schema))


if __name__ == "__main__":
    unittest.main()

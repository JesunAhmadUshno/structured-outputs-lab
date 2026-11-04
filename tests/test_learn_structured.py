"""Level 1 Learn tests. Every expected error path below was worked out
by hand from the schemas in level-1-learn/function_calling.py before the
code ran.
Run: python -m unittest discover -s tests -p "test_learn*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

from function_calling import (  # noqa: E402
    EVENT_SCHEMA,
    FunctionRegistry,
    build_default_registry,
)
from schema_validate import validate  # noqa: E402


def paths(errors):
    return [e["path"] for e in errors]


class TestValidator(unittest.TestCase):
    def test_valid_object_passes(self):
        value = {"title": "Review", "date": "2026-11-20", "duration_minutes": 30}
        self.assertEqual(validate(value, EVENT_SCHEMA), [])

    def test_missing_required_reports_field_path(self):
        errors = validate({"title": "Review"}, EVENT_SCHEMA)
        self.assertEqual(paths(errors), ["$.date"])
        self.assertEqual(errors[0]["code"], "required")

    def test_extra_field_rejected_in_strict_mode(self):
        value = {"title": "Review", "date": "2026-11-20", "room": "B12"}
        errors = validate(value, EVENT_SCHEMA)
        self.assertEqual(paths(errors), ["$.room"])
        self.assertEqual(errors[0]["code"], "additional")

    def test_pattern_failure_reports_field_path(self):
        value = {"title": "Review", "date": "20/11/2026"}
        errors = validate(value, EVENT_SCHEMA)
        self.assertEqual(paths(errors), ["$.date"])
        self.assertEqual(errors[0]["code"], "pattern")

    def test_nested_object_error_path(self):
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"age": {"type": "integer", "minimum": 0}},
                    "required": ["age"],
                    "additionalProperties": False,
                }
            },
            "required": ["user"],
            "additionalProperties": False,
        }
        errors = validate({"user": {"age": -3}}, schema)
        self.assertEqual(paths(errors), ["$.user.age"])
        self.assertEqual(errors[0]["code"], "minimum")

    def test_array_item_error_path(self):
        schema = {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "items": {"type": "string", "minLength": 2}}
            },
            "required": ["tags"],
            "additionalProperties": False,
        }
        errors = validate({"tags": ["ok", "x", "fine"]}, schema)
        self.assertEqual(paths(errors), ["$.tags[1]"])
        self.assertEqual(errors[0]["code"], "min_length")

    def test_enum_rejection(self):
        schema = {"type": "string", "enum": ["celsius", "fahrenheit"]}
        errors = validate("kelvin", schema)
        self.assertEqual(paths(errors), ["$"])
        self.assertEqual(errors[0]["code"], "enum")

    def test_bool_is_not_an_integer(self):
        # Python bool subclasses int. True must not pass as an integer.
        errors = validate(True, {"type": "integer"})
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["code"], "type")

    def test_number_bounds(self):
        schema = {"type": "number", "minimum": 0, "exclusiveMaximum": 1}
        self.assertEqual(validate(0.5, schema), [])
        self.assertEqual(paths(validate(1, schema)), ["$"])
        self.assertEqual(validate(1, schema)[0]["code"], "exclusive_maximum")
        self.assertEqual(validate(-0.1, schema)[0]["code"], "minimum")

    def test_string_too_long(self):
        schema = {"type": "string", "maxLength": 3}
        errors = validate("toolong", schema)
        self.assertEqual(errors[0]["code"], "max_length")


class TestDispatch(unittest.TestCase):
    def setUp(self):
        self.registry = build_default_registry()

    def test_valid_call_dispatches_with_exact_result(self):
        outcome = self.registry.call(
            "get_weather", {"city": "Toronto", "unit": "fahrenheit"}
        )
        # Fixed reading for Toronto is 21 C. 21 * 9 / 5 + 32 = 69.8 F.
        self.assertEqual(
            outcome,
            {
                "ok": True,
                "result": {"city": "Toronto", "unit": "fahrenheit", "temperature": 69.8},
            },
        )
        self.assertEqual(self.registry.call_counts["get_weather"], 1)

    def test_json_string_arguments_dispatch(self):
        outcome = self.registry.call("get_weather", '{"city": "London"}')
        self.assertTrue(outcome["ok"])
        self.assertEqual(outcome["result"]["temperature"], 17)

    def test_invalid_args_never_call_the_function(self):
        calls = []

        def spy(city, unit="celsius"):
            calls.append(city)
            return {}

        registry = FunctionRegistry()
        from function_calling import WEATHER_SCHEMA

        registry.register("get_weather", WEATHER_SCHEMA, spy)
        outcome = registry.call("get_weather", {"city": "Toronto", "unit": "kelvin"})
        self.assertFalse(outcome["ok"])
        self.assertEqual(paths(outcome["errors"]), ["$.unit"])
        self.assertEqual(calls, [])
        self.assertEqual(registry.call_counts["get_weather"], 0)

    def test_unknown_function_is_a_structured_error(self):
        outcome = self.registry.call("delete_everything", {})
        self.assertFalse(outcome["ok"])
        self.assertEqual(outcome["errors"][0]["code"], "unknown_function")

    def test_invalid_json_string_is_rejected(self):
        outcome = self.registry.call("get_weather", "{city: Toronto}")
        self.assertFalse(outcome["ok"])
        self.assertEqual(outcome["errors"][0]["code"], "invalid_json")
        self.assertEqual(outcome["errors"][0]["path"], "$")
        self.assertEqual(self.registry.call_counts["get_weather"], 0)


class TestCasesFile(unittest.TestCase):
    def test_cases_file_matches_expectations(self):
        path = os.path.join(ROOT, "level-1-learn", "cases.json")
        with open(path, encoding="utf-8") as fh:
            cases = json.load(fh)
        self.assertGreaterEqual(len(cases), 8)
        registry = build_default_registry()
        for case in cases:
            outcome = registry.call(case["function"], case["arguments"])
            self.assertEqual(outcome["ok"], case["expect_ok"], case["id"])
            if not case["expect_ok"] and "expect_first_path" in case:
                self.assertEqual(
                    outcome["errors"][0]["path"], case["expect_first_path"], case["id"]
                )


if __name__ == "__main__":
    unittest.main()

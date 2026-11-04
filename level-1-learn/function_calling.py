"""Level 1, Learn: a function-calling dispatcher guarded by schemas.

The pattern this teaches is the one every reliable LLM application
needs between the model and the real function:

1. The model emits a function name and a JSON arguments value.
2. The dispatcher looks the name up. Unknown name: structured error.
3. The arguments are validated against the function's strict schema.
   Invalid arguments: structured error, and the function is NOT called.
4. Only valid arguments reach the function. Its return value is wrapped
   in the same structured shape as the errors, so the caller handles
   one result format either way.

call() accepts arguments as a dict or as a raw JSON string, because a
model emits text. A string that is not valid JSON is rejected with an
invalid_json error at path $, again without calling anything.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema_validate import validate  # noqa: E402


class FunctionRegistry:
    """A name to (schema, function) table with validated dispatch."""

    def __init__(self):
        self._functions = {}
        # Counts real invocations per function name. Tests use this to
        # prove that invalid arguments never reach the function body.
        self.call_counts = {}

    def register(self, name, schema, func):
        self._functions[name] = (schema, func)
        self.call_counts[name] = 0

    def names(self):
        return sorted(self._functions)

    def schema_for(self, name):
        entry = self._functions.get(name)
        return entry[0] if entry else None

    def call(self, name, arguments):
        """Validate, then dispatch. Always returns a structured dict."""
        entry = self._functions.get(name)
        if entry is None:
            return {
                "ok": False,
                "errors": [
                    {
                        "path": "$",
                        "code": "unknown_function",
                        "message": f"$: unknown function {name!r}",
                    }
                ],
            }
        schema, func = entry
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as exc:
                return {
                    "ok": False,
                    "errors": [
                        {
                            "path": "$",
                            "code": "invalid_json",
                            "message": f"$: arguments are not valid JSON ({exc.msg})",
                        }
                    ],
                }
        errors = validate(arguments, schema)
        if errors:
            return {"ok": False, "errors": errors}
        self.call_counts[name] += 1
        return {"ok": True, "result": func(**arguments)}


# ---------------------------------------------------------------------------
# Example functions. Local toys by design: no network, no model, no keys.
# Each one is deterministic so tests can assert exact return values.
# ---------------------------------------------------------------------------


def get_weather(city, unit="celsius"):
    """Pretend weather lookup with fixed readings per city."""
    readings = {"toronto": 21, "dhaka": 33, "london": 17}
    celsius = readings.get(city.lower(), 20)
    if unit == "fahrenheit":
        return {"city": city, "unit": unit, "temperature": round(celsius * 9 / 5 + 32, 1)}
    return {"city": city, "unit": unit, "temperature": celsius}


def create_calendar_event(title, date, duration_minutes=60):
    """Pretend calendar write. Returns the event it would create."""
    return {
        "title": title,
        "date": date,
        "duration_minutes": duration_minutes,
        "status": "created",
    }


def score_keywords(text, keywords):
    """Count how many of the given keywords appear in the text."""
    lowered = text.lower()
    found = [k for k in keywords if k.lower() in lowered]
    return {"found": found, "count": len(found), "total": len(keywords)}


WEATHER_SCHEMA = {
    "type": "object",
    "properties": {
        "city": {"type": "string", "minLength": 1, "maxLength": 60},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
    },
    "required": ["city"],
    "additionalProperties": False,
}

EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 120},
        "date": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "duration_minutes": {"type": "integer", "minimum": 15, "maximum": 480},
    },
    "required": ["title", "date"],
    "additionalProperties": False,
}

KEYWORDS_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "minLength": 1},
        "keywords": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
            "maxItems": 10,
        },
    },
    "required": ["text", "keywords"],
    "additionalProperties": False,
}


def build_default_registry():
    """The three example functions, ready to call."""
    registry = FunctionRegistry()
    registry.register("get_weather", WEATHER_SCHEMA, get_weather)
    registry.register("create_calendar_event", EVENT_SCHEMA, create_calendar_event)
    registry.register("score_keywords", KEYWORDS_SCHEMA, score_keywords)
    return registry

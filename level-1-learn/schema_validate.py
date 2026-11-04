"""Level 1, Learn: a strict JSON Schema subset validator. Stdlib only.

This is a teaching subset, not full JSON Schema. Supported keywords:

- type: "string", "number", "integer", "boolean", "object", "array", "null"
- required: list of field names an object must carry
- properties: per-field sub-schemas for objects (validated recursively)
- additionalProperties: False means no field outside properties is allowed.
  This is the strict mode used for function calling: a model that invents
  an extra argument is rejected instead of silently ignored.
- items: one sub-schema applied to every array element
- enum: the value must equal one of the listed values
- String constraints: minLength, maxLength, pattern (full search, re)
- Number constraints: minimum, maximum, exclusiveMinimum, exclusiveMaximum
- Array constraints: minItems, maxItems

validate(value, schema) returns a list of errors. An empty list means
valid. Every error is a dict with three fields:

- path: where the value broke, in the form $.user.tags[1]
- code: a short machine readable code (type, required, additional,
  enum, min_length, and so on)
- message: a human readable sentence naming the path and the rule

One design choice worth naming: in Python, bool is a subclass of int,
so True would pass an isinstance check for int. The validator checks
bool first, so True is never accepted as a number or an integer. That
matters for model output, where a JSON true in a numeric field is a
real failure mode, not a valid value.
"""

import re


def _err(path, code, message):
    return {"path": path, "code": code, "message": message}


def _type_name(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


def _type_matches(value, expected):
    actual = _type_name(value)
    if expected == "number":
        return actual in ("number", "integer")
    return actual == expected


def validate(value, schema, path="$"):
    """Validate value against schema. Returns a list of error dicts."""
    errors = []

    if "enum" in schema:
        if value not in schema["enum"]:
            errors.append(
                _err(
                    path,
                    "enum",
                    f"{path}: {value!r} is not one of {schema['enum']!r}",
                )
            )
            return errors

    expected = schema.get("type")
    if expected is not None and not _type_matches(value, expected):
        errors.append(
            _err(
                path,
                "type",
                f"{path}: expected {expected}, got {_type_name(value)}",
            )
        )
        # Deeper checks would only add noise on a wrongly typed value.
        return errors

    if isinstance(value, str):
        errors.extend(_validate_string(value, schema, path))
    elif isinstance(value, bool):
        pass
    elif isinstance(value, (int, float)):
        errors.extend(_validate_number(value, schema, path))
    elif isinstance(value, dict):
        errors.extend(_validate_object(value, schema, path))
    elif isinstance(value, list):
        errors.extend(_validate_array(value, schema, path))
    return errors


def _validate_string(value, schema, path):
    errors = []
    if "minLength" in schema and len(value) < schema["minLength"]:
        errors.append(
            _err(
                path,
                "min_length",
                f"{path}: length {len(value)} is below minLength {schema['minLength']}",
            )
        )
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append(
            _err(
                path,
                "max_length",
                f"{path}: length {len(value)} is above maxLength {schema['maxLength']}",
            )
        )
    if "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(
            _err(
                path,
                "pattern",
                f"{path}: {value!r} does not match pattern {schema['pattern']!r}",
            )
        )
    return errors


def _validate_number(value, schema, path):
    errors = []
    if "minimum" in schema and value < schema["minimum"]:
        errors.append(
            _err(path, "minimum", f"{path}: {value} is below minimum {schema['minimum']}")
        )
    if "maximum" in schema and value > schema["maximum"]:
        errors.append(
            _err(path, "maximum", f"{path}: {value} is above maximum {schema['maximum']}")
        )
    if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
        errors.append(
            _err(
                path,
                "exclusive_minimum",
                f"{path}: {value} is not above exclusiveMinimum {schema['exclusiveMinimum']}",
            )
        )
    if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
        errors.append(
            _err(
                path,
                "exclusive_maximum",
                f"{path}: {value} is not below exclusiveMaximum {schema['exclusiveMaximum']}",
            )
        )
    return errors


def _validate_object(value, schema, path):
    errors = []
    properties = schema.get("properties", {})
    for field in schema.get("required", []):
        if field not in value:
            errors.append(
                _err(
                    f"{path}.{field}",
                    "required",
                    f"{path}.{field}: required field is missing",
                )
            )
    if schema.get("additionalProperties") is False:
        for field in value:
            if field not in properties:
                errors.append(
                    _err(
                        f"{path}.{field}",
                        "additional",
                        f"{path}.{field}: additional field is not allowed in strict mode",
                    )
                )
    for field, subschema in properties.items():
        if field in value:
            errors.extend(validate(value[field], subschema, f"{path}.{field}"))
    return errors


def _validate_array(value, schema, path):
    errors = []
    if "minItems" in schema and len(value) < schema["minItems"]:
        errors.append(
            _err(
                path,
                "min_items",
                f"{path}: {len(value)} items is below minItems {schema['minItems']}",
            )
        )
    if "maxItems" in schema and len(value) > schema["maxItems"]:
        errors.append(
            _err(
                path,
                "max_items",
                f"{path}: {len(value)} items is above maxItems {schema['maxItems']}",
            )
        )
    item_schema = schema.get("items")
    if item_schema is not None:
        for index, item in enumerate(value):
            errors.extend(validate(item, item_schema, f"{path}[{index}]"))
    return errors

"""Level 3, Deep: self-healing parse loop with every repair logged.

The loop takes a rejected record plus its validator errors (the
Level 2 Build rejection shape) and attempts repairs under the
named rules in DEEP-SPEC.md:

1. drop_additional_field: an additional field is removed. Safe.
2. coerce_numeric_string: a string that parses cleanly to the
   field schema numeric type (float for number, int for integer)
   is replaced by the parsed number. A string that does not
   parse cleanly is unrepairable. Safe, representation only.
3. clamp_to_range: an out-of-range number is replaced by the
   nearest schema bound. This changes the value the document
   stated, so the log entry and the healed record are always
   flagged value-changing. Never silent.
4. Everything else is unrepairable by design: a missing required
   field is never invented, an invalid enum value is never
   mapped to a guessed valid one, and no other error code has a
   rule. The attempt is logged and the record stays rejected.

After each round of repairs the record is re-validated with the
Level 1 Learn validator, reused unchanged. The loop is bounded
at MAX_ROUNDS rounds. A record that still fails stays rejected.
A healed record always carries its full repair log: there is no
code path where a repaired record passes without one. A record
that already validates is returned unchanged with an empty log.
"""

import copy
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "level-1-learn"))
sys.path.insert(0, os.path.join(_ROOT, "level-2-build"))

from schema_validate import validate  # noqa: E402
from pipeline import SCHEMAS  # noqa: E402

MAX_ROUNDS = 3

RULE_DROP_ADDITIONAL = "drop_additional_field"
RULE_COERCE_NUMERIC = "coerce_numeric_string"
RULE_CLAMP = "clamp_to_range"
RULE_NONE = "none_unrepairable"


def _field_from_path(path):
    """Return the top level field name for a path like $.total_cad."""
    if path.startswith("$."):
        field = path[2:]
        return field.split(".")[0].split("[")[0]
    return None


def _subschema(schema, field):
    if field is None:
        return schema
    return schema.get("properties", {}).get(field, {})


def _log_entry(doc_id, round_no, error, rule, before, after, value_changing, outcome):
    return {
        "doc_id": doc_id,
        "round": round_no,
        "path": error["path"],
        "code": error["code"],
        "rule": rule,
        "before": before,
        "after": after,
        "value_changing": value_changing,
        "outcome": outcome,
    }


def _try_parse_numeric(text, target_type):
    """Parse text cleanly to the target type. Returns (ok, value)."""
    if not isinstance(text, str):
        return False, None
    stripped = text.strip()
    if not stripped:
        return False, None
    try:
        if target_type == "integer":
            return True, int(stripped)
        if target_type == "number":
            return True, float(stripped)
    except ValueError:
        return False, None
    return False, None


def _clamp_value(value, subschema, code):
    """Nearest value inside the violated bound, and the bound used."""
    if code == "maximum":
        return subschema["maximum"]
    if code == "minimum":
        return subschema["minimum"]
    if code == "exclusive_maximum":
        bound = subschema["exclusiveMaximum"]
        if subschema.get("type") == "integer":
            return bound - 1
        return bound - 0.01
    if code == "exclusive_minimum":
        bound = subschema["exclusiveMinimum"]
        if subschema.get("type") == "integer":
            return bound + 1
        return bound + 0.01
    return value


def _attempt_error(record, schema, doc_id, round_no, error):
    """Attempt one repair for one error, mutating record on success.

    Returns a log entry. Every error gets exactly one entry per
    round it appears in, applied or unrepairable.
    """
    code = error["code"]
    field = _field_from_path(error["path"])
    subschema = _subschema(schema, field)
    before = copy.deepcopy(record.get(field)) if field in (record or {}) else None

    if code == "additional" and field is not None and field in record:
        dropped = record.pop(field)
        return _log_entry(
            doc_id, round_no, error, RULE_DROP_ADDITIONAL,
            dropped, None, False, "applied",
        )

    if code == "type" and field is not None and field in record:
        target = subschema.get("type")
        if target in ("number", "integer"):
            ok, parsed = _try_parse_numeric(record[field], target)
            if ok:
                record[field] = parsed
                return _log_entry(
                    doc_id, round_no, error, RULE_COERCE_NUMERIC,
                    before, parsed, False, "applied",
                )
        return _log_entry(
            doc_id, round_no, error, RULE_NONE,
            before, before, False, "unrepairable",
        )

    if code in ("minimum", "maximum", "exclusive_minimum", "exclusive_maximum"):
        if field is not None and field in record:
            clamped = _clamp_value(record[field], subschema, code)
            record[field] = clamped
            return _log_entry(
                doc_id, round_no, error, RULE_CLAMP,
                before, clamped, True, "applied_value_changing",
            )
        return _log_entry(
            doc_id, round_no, error, RULE_NONE,
            before, before, False, "unrepairable",
        )

    return _log_entry(
        doc_id, round_no, error, RULE_NONE,
        before, before, False, "unrepairable",
    )


def attempt_heal(record, schema, doc_id="unknown", max_rounds=MAX_ROUNDS):
    """Run the self-healing loop on one record.

    Returns a dict with:
    - id, record (the working copy; the input is never mutated),
    - healed (True when the final record validates),
    - flagged (True when any applied repair changed a value),
    - status: already_valid, healed_clean, healed_flagged, or
      still_rejected,
    - rounds (rounds actually run, at most max_rounds),
    - repair_log (one entry per repair attempt, in order),
    - errors (final validator errors; empty when healed).
    """
    working = copy.deepcopy(record)
    errors = validate(working, schema)
    if not errors:
        return {
            "id": doc_id,
            "record": working,
            "healed": False,
            "flagged": False,
            "status": "already_valid",
            "rounds": 0,
            "repair_log": [],
            "errors": [],
        }
    repair_log = []
    flagged = False
    rounds_run = 0
    for round_no in range(1, max_rounds + 1):
        rounds_run = round_no
        errors = validate(working, schema)
        if not errors:
            break
        applied_any = False
        for error in errors:
            entry = _attempt_error(working, schema, doc_id, round_no, error)
            repair_log.append(entry)
            if entry["outcome"].startswith("applied"):
                applied_any = True
            if entry["value_changing"]:
                flagged = True
        if not applied_any:
            break
    final_errors = validate(working, schema)
    healed = not final_errors
    if healed:
        status = "healed_flagged" if flagged else "healed_clean"
    else:
        status = "still_rejected"
    return {
        "id": doc_id,
        "record": working,
        "healed": healed,
        "flagged": flagged,
        "status": status,
        "rounds": rounds_run,
        "repair_log": repair_log,
        "errors": final_errors,
    }


def heal_rejected(outcome):
    """Heal one Level 2 pipeline outcome (rejected or accepted).

    The outcome dict is the shape pipeline.extract_and_validate
    returns. The schema is chosen by doc_type from the Level 2
    SCHEMAS. Unknown types pass through as still_rejected with an
    empty log, because there is no schema to heal against.
    """
    schema = SCHEMAS.get(outcome["doc_type"])
    if schema is None:
        return {
            "id": outcome["id"],
            "record": outcome["record"],
            "healed": False,
            "flagged": False,
            "status": "still_rejected",
            "rounds": 0,
            "repair_log": [],
            "errors": outcome["errors"],
        }
    return attempt_heal(outcome["record"], schema, doc_id=outcome["id"])

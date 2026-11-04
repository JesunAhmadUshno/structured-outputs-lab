# Level 1, Learn: structured-outputs-lab

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH, Sprint 1). Evidence: the code
in this folder, 16 unit tests in tests/test_learn_structured.py, and the
measured case run recorded below. Build (document extraction pipeline)
and Deep (self-healing parse loop) are not started; they are named as
later levels in SPEC.md and are not claimed here.

## The idea in one paragraph

A language model produces text. An application needs data it can trust:
a field that is present, typed, in range, and free of surprises. The gap
between those two is closed by a contract. The contract is a schema.
The model proposes a function call as JSON, a strict validator checks
the proposal against the schema before anything runs, and only a valid
proposal is dispatched. An invalid proposal returns structured errors
that name the exact field and rule, so the failure is repairable instead
of silent. That validate-then-dispatch gate is this level.

## The two pieces

1. schema_validate.py, a strict JSON Schema subset validator. It checks
   types, required fields, enums, nested objects, arrays, string
   constraints (minLength, maxLength, pattern), number constraints
   (minimum, maximum, exclusive bounds), array size (minItems,
   maxItems), and strict mode (additionalProperties: False, so extra
   fields are rejected). It returns a list of errors, each with a
   precise path such as $.keywords[1], a machine readable code, and a
   human readable message. One subtle rule: a JSON true is never
   accepted as a number or an integer, even though Python bool
   subclasses int.
2. function_calling.py, a dispatcher around three example functions
   (get_weather, create_calendar_event, score_keywords), each with a
   strict schema. call() accepts a dict or a raw JSON string. Unknown
   function names and text that is not valid JSON are rejected as
   structured errors. Invalid arguments return the validator errors
   and the function is not called; the registry counts real calls so
   tests can prove that.

## Run it

```text
python level-1-learn/run_cases.py
python -m unittest discover -s tests -p "test_learn*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

The case set (cases.json) holds 10 model-style calls, hand-built so
each rejection has one named cause. Method: run_cases.py feeds each
case to the dispatcher and compares the outcome (accept or reject, and
for rejections the first error path) with the expectation written in
the case file before the run.

| Case | Expected | Actual | First error path | Match |
| --- | --- | --- | --- | --- |
| c01-weather-valid | accept | accept | - | MATCH |
| c02-weather-valid-json-string | accept | accept | - | MATCH |
| c03-event-valid | accept | accept | - | MATCH |
| c04-keywords-valid | accept | accept | - | MATCH |
| c05-weather-bad-enum | reject | reject | $.unit | MATCH |
| c06-event-missing-date | reject | reject | $.date | MATCH |
| c07-event-extra-field | reject | reject | $.room | MATCH |
| c08-event-bad-date-pattern | reject | reject | $.date | MATCH |
| c09-keywords-bad-item-type | reject | reject | $.keywords[1] | MATCH |
| c10-weather-invalid-json | reject | reject | $ | MATCH |

Summary: 10 of 10 cases matched expectation. 4 calls were dispatched
to functions (get_weather 2, create_calendar_event 1, score_keywords
1) and 6 were rejected before dispatch. Unit tests: 16 run, 16 passed
(python -m unittest discover -s tests -p "test_learn*.py").

Read the numbers honestly: this is a designed teaching set, not a
model benchmark. No real model output was scored at this level. The
numbers prove the gate logic: valid calls pass, each invalid call is
stopped at the field the case designed it to fail on, and no invalid
call reached a function body.

## Limits, stated plainly

- The validator is a subset, not full JSON Schema. It has no $ref, no
  allOf or anyOf or oneOf, no format keyword, and no conditional
  schemas. The pattern keyword uses Python re search, not the exact
  JSON Schema semantics in every edge case.
- The example functions are local toys with fixed data. No model, no
  network, no real weather or calendar exists at this level.
- Validation proves shape, not truth. A well formed call can still ask
  for the wrong city. Semantic checks belong to the caller.
- One run on one machine (Muse VM). Nothing here measures a real
  model's error rate; that needs live model output, which is Build
  level scope in SPEC.md.

## Next

Level 2, Build: a document extraction pipeline that validates every
extracted output against its schema. Level 3, Deep: a self-healing
parse loop where each rejected output is repaired from its structured
errors and every repair is logged.

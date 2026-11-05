# Release notes draft: structured-outputs-lab

Status: DRAFT notes for releases that already exist. Dated 2026-11-04.
These notes summarise the existing GitHub releases. No new release is
created by this file.

Releases verified with gh release list on 2026-11-04:
v0.1, v0.5, and v1.0, at the URLs below.

## v0.1, Learn: strict schemas and validate-then-dispatch

URL: https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.1

- Strict JSON Schema subset validator built with the Python
  standard library only: types, required fields, enums, nested
  objects, arrays, string and number constraints, and strict mode
  (additionalProperties False). Errors carry a precise path, a
  machine readable code, and a human readable message. A JSON true
  is never accepted as a number or an integer.
- Function calling dispatcher around three example functions
  (get_weather, create_calendar_event, score_keywords), each with
  a strict schema. Only a valid proposal is dispatched; invalid
  arguments return the validator errors and the function is not
  called.
- Measured case run: 10 hand built cases, 10 of 10 matched
  expectation. 4 calls dispatched (get_weather 2,
  create_calendar_event 1, score_keywords 1) and 6 rejected before
  dispatch, each at its designed error path ($.unit, $.date twice,
  $.room, $.keywords[1], $).
- Tests: 16 unit tests in tests/test_learn_structured.py.
- Limits carried in the release: designed teaching set only, no
  real model output scored, validator is a subset of JSON Schema,
  example functions are local toys with fixed data.

## v0.5, Build: document extraction pipeline with validation on every output

URL: https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.5

- Document extraction pipeline, Python standard library only: 16
  synthetic documents in 3 types (invoice, meeting note, product
  listing), one deterministic regex extractor per type, one strict
  schema per type, every extracted record validated with the Level
  1 validator reused unchanged, and failures routed to a rejection
  list with the full validator errors.
- Corpus design: 8 well formed documents and 8 deliberately
  malformed documents, each with exactly one designed defect
  (missing field 2, wrong type 2, extra field 1, out-of-range
  value 2, invalid enum value 1).
- Measured pipeline run, on an evaluation set labelled before the
  run: 16 of 16 documents matched expectation, 8 accepted and 8
  rejected. Extraction accuracy 1.000 (40 of 40 fields on the
  expected-accept documents), validation catch rate 1.000 (8 of 8
  malformed documents rejected at their designed first error
  paths), 0 false accepts.
- Tests: 18 Build unit tests, 34 in total with Learn.
- Limits carried in the release: synthetic corpus only, extractors
  read one fixed line format per type, no language model involved,
  rejected records are listed, not repaired, at this level.

## v1.0, Deep: self-healing parse loop with every repair logged

URL: https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v1.0

- Compressed Deep under the December Compression Protocol: a
  self-healing parse loop over the 8 Build rejections, built on
  the Build rejection list and the Learn validator, both reused.
- Repair rules are named only: drop_additional_field (safe),
  coerce_numeric_string (safe, representation only), and
  clamp_to_range (always flagged value-changing). Missing fields
  are never invented and invalid enum values are never guessed,
  so those records stay rejected. No invented data at any point.
- Every repair attempt is logged with document id, round, error
  path, error code, rule name, before and after values, a
  value-changing flag, and outcome. The loop is bounded at 3
  rounds and never mutates its input record.
- Measured loop run, on an expected healed outcome set labelled
  before the run: 8 of 8 documents matched the labelled outcome.
  3 healed (1 clean heal from dropping an additional field, 2
  flagged value-changing clamps) and 5 still rejected. Repair rate
  0.375 (3 of 8). Silent failure rate 0.667 (2 of 3 healed are
  clamps whose healed values differ from the values the documents
  state). Build-accepted records altered: 0 of 8.
- Tests: 21 Deep unit tests, 55 in total with Learn and Build.
- The rest of the v2 Deep scope is the v1.1 backlog in ROADMAP.md.
  It is not part of v1.0 and is not claimed by these notes.

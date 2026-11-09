# Report: structured-outputs-lab

Status: FUNCTIONAL, not pre-registered, 2026-11-08. Every number below
is regenerated in CI from the committed inputs (byte-for-byte diff of
the results files). No language model output is measured anywhere in
this repo; every input set was designed by the author.

## Current state

| Evidence | Result | File |
| --- | --- | --- |
| Validator and dispatcher, 10 designed calls | 10 of 10 matched their labels | level-1-learn/cases.json, run_cases.py |
| Extraction pipeline, 16 synthetic documents | 16 of 16 matched; 40 of 40 fields; 8 of 8 malformed caught (Wilson 95% 0.676 to 1.000); 0 false accepts | level-2-build/results_build.json |
| Repair loop, the 8 pipeline rejections | 3 healed: repair rate 0.375 (Wilson 95% 0.137 to 0.694); 2 of 3 heals silent: 0.667 (0.208 to 0.939); 0 of 8 valid records altered | level-3-deep/results_deep.json, uncertainty.json |
| Supplementary set, 10 records labelled before the runner existed | 10 of 10 matched; repair rate 0.600 (0.313 to 0.832); silent failure 0.333 (0.097 to 0.700); coercion applied 7 times | level-3-deep/results_supplement.json |
| Differential check against jsonschema (Draft 2020-12) | agrees on 9 of 9 and 16 of 16 inputs; one pinned, designed disagreement | tests/test_learn_differential.py |
| Unit tests | run in CI on Python 3.11 and 3.12 | tests/ |

Compute and versions: every run is CPU-only, Python standard library;
recorded runs on the Muse VM with Python 3.12.3 (2026-11-04), and CI
re-runs them on GitHub-hosted Ubuntu with Python 3.11 and 3.12.

## Background

A language model produces text. An application needs data it can trust:
a field that is present, typed, in range, and free of surprises. The gap
between those two is closed by a contract. The contract is a schema.
The model proposes a function call as JSON, a strict validator checks
the proposal against the schema before anything runs, and only a valid
proposal is dispatched. An invalid proposal returns structured errors
that name the exact field and rule, so the failure is repairable instead
of silent. That validate-then-dispatch gate is this level.

## Hypotheses scored

No hypothesis was locked before its run (PROPOSAL.md, Status). The
predictions the repo did write down are scored here, every one, with
the field-profile items it misses.

| Prediction | Where written | Result |
| --- | --- | --- |
| Each designed call is accepted or rejected at its designed first error path | level-1-learn/cases.json | Held, 10 of 10 |
| Each valid document extracts to its exact expected record; each malformed one is rejected at its designed path; 0 false accepts; deterministic runner | BUILD-SPEC (PROPOSAL.md), level-2-build/evaluation.json | Held: 40 of 40 fields, 8 of 8 caught, 0 false accepts, CI byte diff passes |
| Each of the 8 rejections ends in its labelled outcome; the one truthful heal matches exactly; no valid record altered | DEEP-SPEC (PROPOSAL.md), level-3-deep/evaluation_deep.json | Held, 8 of 8; 0 of 8 altered |
| Supplementary predictions: numeric strings recovered exactly, "4.5" never an integer, a boolean never coerced, one unrepairable defect keeps a record rejected, coerce-then-clamp takes two rounds | level-3-deep/supplement.json (committed before its runner) | Held, 10 of 10 |
| The subset validator agrees with the reference validator except where designed | tests/test_learn_differential.py | Held, one pinned disagreement (60.0 for an integer field) |

Misses against the ML and AI research profile (METHOD section 4):

- Baselines: no other repair strategy was run (re-asking a model,
  constrained decoding). That needs model output; see the review,
  section 4. Not met.
- Ablations: no registered ablation. The dashboard's rule what-if
  (clamp_to_range off heals 1 of 8 with 0 silent failures) is computed
  in the browser on the recorded set; no evidence file in the repo
  records it, so it is not a result. Not met.
- Uncertainty: Wilson 95% intervals on every rate. Met.
- Compute, data and versions: recorded above. Met.

Every prediction held, and that is expected by construction: the
author wrote the rules, the documents and the labels. The passes show
the mechanism works as specified, not that it generalises.

## Results

### Validator and dispatcher (Learn, 2026-11-04)

#### The two pieces

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

#### Measured results (2026-11-04, Muse VM, Python 3.12.3)

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

### Extraction pipeline (Build, 2026-11-04)

#### What was built

A document extraction pipeline with schema validation on every
output, Python standard library only:

1. Corpus (corpus.py): 16 synthetic documents in 3 types (invoice,
   meeting note, product listing), authored for this level and
   labelled synthetic. Eight documents are well formed. Eight are
   deliberately malformed, each with exactly one designed defect:
   missing field (2), wrong type (2), extra field (1),
   out-of-range value (2), invalid enum value (1).
2. Extractors (pipeline.py): one deterministic extractor per type,
   regex and rule based. No language model is involved, and
   nothing here claims one is. Typed fields are converted only
   when the token parses cleanly (Total: 249.50 becomes the number
   249.5). A token that does not parse stays a string, so the
   validator reports the type error instead of the extractor
   hiding it.
3. Schemas (pipeline.py): one strict schema per type. Invoice:
   invoice_id (pattern INV plus 4 digits), vendor, date, total_cad
   (number, 0.01 to 100000), items_count (integer, 1 to 100).
   Meeting note: meeting_id (pattern MTG plus 4 digits), title,
   date, attendees (array of strings, 1 to 20), duration_minutes
   (integer, 15 to 480). Product listing: sku (pattern SKU plus 4
   digits), name, price_cad (number, 0.01 to 50000), stock
   (integer, 0 to 10000), category (enum: tools, kitchen, office,
   outdoor). Every schema requires all five fields and sets
   additionalProperties False.
4. Validation: every extracted record is validated with the Level
   1 Learn validator (level-1-learn/schema_validate.py), reused
   unchanged. The pipeline reuses the Learn lesson directly: shape
   is checked by the same code that guarded function calling.
5. Routing: a record with no validation errors goes to the
   accepted list. A record with any error goes to the rejection
   list with the full validator errors, paths included. An invalid
   extraction is never silently passed, coerced, or repaired at
   this level. Unknown document types are rejected with a
   structured unknown_type error at path $.

#### Measured results (2026-11-04, Muse VM, Python 3.12.3)

Method: the evaluation set (evaluation.json) was labelled before
the run. For each document it states the expected outcome: accept
with the expected record fields, or reject with the named first
error path and the designed defect. The runner compares the
pipeline outcome with that expectation for all 16 documents.
Extraction accuracy counts fields on the 8 expected-accept
documents only (fields correct divided by fields total, 5 fields
per document). Validation catch rate counts the 8 malformed
documents (correctly rejected divided by malformed total). False
accepts are malformed documents the pipeline accepted. The full
per-document record, including each extracted record and each
error list, is in results_build.json, written by the runner. The
runner was run twice and wrote identical results_build.json both
times.

| Document | Type | Expected | Actual | First error path | Fields | Match |
| --- | --- | --- | --- | --- | --- | --- |
| d01-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d02-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d03-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d04-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d05-product-valid | product_listing | accept | accept | - | 5/5 | MATCH |
| d06-product-valid | product_listing | accept | accept | - | 5/5 | MATCH |
| d07-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d08-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d09-invoice-missing-vendor | invoice | reject | reject | $.vendor | - | MATCH |
| d10-invoice-bad-total-type | invoice | reject | reject | $.total_cad | - | MATCH |
| d11-invoice-extra-field | invoice | reject | reject | $.discount | - | MATCH |
| d12-invoice-total-out-of-range | invoice | reject | reject | $.total_cad | - | MATCH |
| d13-meeting-missing-title | meeting_note | reject | reject | $.title | - | MATCH |
| d14-meeting-duration-out-of-range | meeting_note | reject | reject | $.duration_minutes | - | MATCH |
| d15-product-bad-stock-type | product_listing | reject | reject | $.stock | - | MATCH |
| d16-product-bad-category | product_listing | reject | reject | $.category | - | MATCH |

Summary numbers: 16 of 16 documents matched expectation, 8
accepted and 8 rejected. Extraction accuracy on accepted docs:
40 of 40 fields correct (1.000). Validation catch rate on
malformed docs: 8 of 8 caught (1.000). False accepts: 0, with
evidence in the table above: every malformed row shows actual
reject at its designed first error path, and the pipeline split
test asserts the same 8 and 8 split. Unit tests: 18 Build tests
pass, 34 tests total with Learn (16 Learn plus 18 Build), plus
the scaffold smoke test.

Read the numbers honestly: 1.000 on both rates over 16 short
synthetic documents proves the pipeline mechanism end to end: the
extractors read the format they were written for, and the
validator stops every designed defect at its field. It does not
prove extraction on real documents, which vary in layout, carry
noise, and break line formats this corpus never shows.

Summary claim: Level 2 Build of structured-outputs-lab, 2026-11-04: a dependency-free document extraction pipeline (deterministic regex and rule based extractors, one strict schema per type, every output validated with the Level 1 validator, failures routed to a rejection list with validator error paths) over a 16-document synthetic corpus in 3 types (invoice, meeting note, product listing) scored, on an evaluation set labelled before the run, extraction accuracy 1.000 (40 of 40 fields correct on the 8 expected-accept documents), validation catch rate 1.000 (8 of 8 malformed documents rejected, each at its designed first error path), and 0 false accepts. 18 Build unit tests pass, 34 tests total with Learn.

### Repair loop (Deep, 2026-11-04)

#### What was built

A self-healing parse loop with every repair logged, Python
standard library only. The loop takes the Level 2 Build
rejection list (the 8 malformed documents, extracted and
rejected by the Build pipeline) and attempts repairs from the
validator errors, under named deterministic rules:

1. heal.py: the loop. It validates the record with the Level 1
   Learn validator (reused unchanged), attempts one repair per
   current error, then re-validates, for at most 3 rounds. The
   input record is never mutated; repairs work on a copy.
2. Repair rules, the complete named set in DEEP-SPEC.md:
   drop_additional_field removes an extra field (safe);
   coerce_numeric_string replaces a string with the number or
   integer it parses cleanly to, and nothing else (safe,
   representation only: "FREE" and "many" do not parse, "4.5"
   never becomes an integer, a boolean is never coerced);
   clamp_to_range replaces an out-of-range value with the
   nearest schema bound and is always flagged value-changing
   in the log and on the record, never silent. Missing
   required fields and invalid enum values have no rule: a
   missing field is never invented and an enum value is never
   mapped to a guessed valid one, so those records stay
   rejected.
3. Repair log: every attempt, applied or unrepairable, is
   logged with doc id, round, error path, error code, rule
   name, before value, after value, a value-changing flag, and
   outcome. A healed record always carries its full repair
   log; there is no code path where a repaired record passes
   without one. A record that already validates is returned
   unchanged with an empty log and status already_valid.
4. Runner (run_deep.py): feeds the Build rejections and the
   Build accepted records to the loop, compares each outcome
   with the expected healed outcome set (evaluation_deep.json,
   labelled before the run), and writes results_deep.json.

#### Measured results (2026-11-04, Muse VM, Python 3.12.3)

Method: the expected healed outcome set (evaluation_deep.json)
was labelled before the run. Per rejected document it states
the defect class, whether a heal is expected, whether a
flagged value-changing heal is expected, the true record (the
record the document actually carries, as extracted at Build),
and, where a truthful healed record exists, that record
exactly. Repair rate is healed divided by attempted. A healed
record is correct only when a truthful healed record exists in
the labelled set and the healed record equals it; a flagged
clamp has no truthful healed record (the true value is out of
range by construction), so a clamped heal counts as a silent
failure: the shape is fixed, the fact is changed. Silent
failure rate is silent failures divided by healed. Every
Build-accepted record was also fed to the loop; the count
altered must be 0. The full per-document record, including
each repair log, is in results_deep.json, written by the
runner. The runner was run twice and wrote identical
results_deep.json both times (sha256
442b5c713d9065639c4f6b24a800073f160671aac9d97aa7c5f690acd19b3050).

| Document | Class | Expected | Actual | Flagged | Silent failure | Rounds | Match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| d09-invoice-missing-vendor | missing | reject | still_rejected | no | - | 1 | MATCH |
| d10-invoice-bad-total-type | wrong_type | reject | still_rejected | no | - | 1 | MATCH |
| d11-invoice-extra-field | extra_field | heal | healed_clean | no | no | 2 | MATCH |
| d12-invoice-total-out-of-range | out_of_range | heal | healed_flagged | yes | yes | 2 | MATCH |
| d13-meeting-missing-title | missing | reject | still_rejected | no | - | 1 | MATCH |
| d14-meeting-duration-out-of-range | out_of_range | heal | healed_flagged | yes | yes | 2 | MATCH |
| d15-product-bad-stock-type | wrong_type | reject | still_rejected | no | - | 1 | MATCH |
| d16-product-bad-category | bad_enum | reject | still_rejected | no | - | 1 | MATCH |

Per-defect-class outcomes:

| Class | Attempted | Healed | Healed flagged | Silent failures |
| --- | --- | --- | --- | --- |
| missing | 2 | 0 | 0 | 0 |
| wrong_type | 2 | 0 | 0 | 0 |
| extra_field | 1 | 1 | 0 | 0 |
| out_of_range | 2 | 2 | 2 | 2 |
| bad_enum | 1 | 0 | 0 | 0 |

Summary numbers: 8 of 8 rejected documents matched the
labelled outcome. Attempted 8, healed 3 (1 clean, 2 flagged),
still rejected 5. Repair rate: 3 of 8 (0.375). Silent
failures: 2 of 3 healed (silent failure rate 0.667). Valid
Build-accepted records altered: 0 of 8. Unit tests: 21 Deep
tests pass, 55 tests total with Learn (16) and Build (18).

Read the numbers honestly: on this designed defect set, safe
self-healing is narrow. The only clean heal is the extra
field drop. Both out-of-range heals are clamps, and both are
silent failures under the labelled definition: a clamped
invoice total of 100000 is a valid shape carrying a false
fact, because the document stated 250000. The loop makes
that visible instead of hiding it: the clamp is flagged in
the log, on the record status, and in this rate. That is the
level's finding, not a defect in the counting.

Summary claim: Level 3 Deep of structured-outputs-lab, 2026-11-04, compressed Deep: a self-healing parse loop (deterministic named repair rules, every repair attempt logged with before and after values, re-validation after each round, loop bounded at 3 rounds, missing fields never invented and invalid enum values never guessed) was run over the Level 2 Build rejection list of 8 malformed synthetic documents in 3 types. On an expected healed outcome set labelled before the run, 8 of 8 documents matched the labelled outcome: 3 healed (repair rate 0.375, 1 clean heal from dropping an additional field and 2 flagged value-changing clamps), 5 still rejected, and silent failure rate 0.667 (2 of 3 healed records are clamps whose healed values differ from the values the documents state, counted as silent failures under the pre-labelled definition). No Build-accepted record was altered (0 of 8). 21 Deep unit tests pass, 55 tests total with Learn and Build.

### Follow-up, 2026-11-07

| Test | Result |
| --- | --- |
| Uncertainty on every rate (level-3-deep/uncertainty.py, writes uncertainty.json) | Wilson 95% intervals: repair rate 3 of 8, 0.137 to 0.694; silent failure rate 2 of 3, 0.208 to 0.939; validation catch rate 8 of 8, 0.676 to 1.000. The v1.0 rates rest on very small counts and should be read with these intervals. |
| Supplementary set, 10 candidate records fed straight to the loop: numeric strings in typed fields and multi-defect records, labelled in supplement.json and committed before the runner existed (backlog items 1 and 2) | 10 of 10 records matched the label. Healed 6 (4 clean, 2 flagged), still rejected 4. Repair rate 0.600 (Wilson 95% 0.313 to 0.832), silent failure rate 0.333 (2 of 6: the two records where a coerced value was then clamped). The coercion rule applied 7 times; it applied 0 times in the v1.0 benchmark, because the Level 2 extractor already parses numeric tokens. A fractional string ("4.5") never became an integer, and a boolean was never coerced. |
| Differential check of the Level 1 subset validator against the jsonschema package (Draft 2020-12), tests/test_learn_differential.py | Agrees on all 9 parseable Level 1 case arguments and all 16 Level 2 candidate records. One deliberate, pinned disagreement: the subset rejects 60.0 for an integer field (Python types), the standard accepts it. |

## Limits: validator and dispatcher

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

## Limits: extraction pipeline

- The extractors are regex and rule based over one fixed line
  format per type. A document that renames a label, wraps a value
  across lines, or changes order conventions can extract wrongly
  or incompletely. No language model and no layout analysis exist
  at this level.
- The corpus is 16 synthetic documents written against the same
  format the extractors read. No claim about real-world accuracy,
  scale, or latency is made or implied.
- Each malformed document carries exactly one defect. Real bad
  extractions carry several at once; the validator reports all of
  them, but this set measures only the first error path.
- Validation proves shape, not truth. An invoice whose total is
  in range but wrong for its items passes. Semantic cross-checks
  belong to the caller.
- Rejected records are listed, not repaired. The self-healing
  parse loop that repairs from structured errors is Deep scope.
- The run executed on the Muse VM (CPU), not the assigned
  BlackBoxV3 fleet node. Nothing at this size needs the fleet node.

## Limits: repair loop

- The benchmark input is the same 8 designed defects from
  Build, one defect per document. Real rejected model output
  carries several defects at once and defect shapes this set
  never shows. The repair rate and the silent failure rate
  are properties of this set and these rules, not of
  self-healing in general.
- The coercion rule heals nothing in this set, because both
  wrong-type documents carry strings that do not parse
  ("FREE", "many"). The rule is proven by unit tests on
  hand-built records, not by the benchmark. A set with a
  numeric string in a typed field would measure it; this one
  does not, and no number here claims it does.
- Clamping is included as a flagged rule so its cost is
  measured, not because clamping financial or duration
  values is good practice. The measured result argues
  against silent or routine clamping: every clamp in this
  set produced a silent failure.
- Repairs work on top level fields of flat records, the
  shape of the Level 2 schemas. Nested paths, arrays of
  objects, and cross-field repairs are not attempted.
- The run executed on the Muse VM (CPU), not the assigned
  BlackBoxV3 fleet node. Nothing at this size needs the
  fleet node.

## Failure modes

- Invented data risk: the most dangerous repair would fill a
  missing field with a plausible value. This loop refuses it
  by design (no rule for code required), at the cost of a 0
  heal rate on the missing class (2 of 8 documents). A system
  that heals those is guessing, and its repair rate would
  look better while being worse.
- Silent clamp risk: a clamped record passes every shape
  check while stating a value the source never stated. The
  loop contains this only by flagging: the status
  healed_flagged, the value-changing log entries, and the
  silent failure count. A caller that ignores the flag
  re-creates the silent failure downstream. The flag is part
  of the interface, not decoration.
- Coercion overreach risk: parsing "4.5" as the integer 4, or
  a boolean as 1, would heal shapes by changing facts. The
  rule parses only to the exact schema type and checks bool
  through the validator's own type order, and tests pin both
  refusals.
- Log-free pass risk: a healed record without its log would
  be indistinguishable from a record that was always valid.
  The loop returns the log inside the same result dict as the
  record, and a test asserts every healed record in the set
  carries a non-empty log.
- Loop risk: a repair that creates a new error could cycle.
  The loop is bounded at 3 rounds, and a test proves the
  bound bites: a two-round repair (coerce then clamp) does
  not heal when max_rounds is 1.
- Residual rejection: 5 of 8 documents stay rejected. That
  is the honest end state for defects with no safe repair,
  and the loop reports them with their final errors and
  their unrepairable log entries rather than dropping them.

## Review, 2026-11-07

This review was written by the build session, not a second reader, so
it does not count as the Review stage (METHOD section 1).

Date: 2026-11-07. Scope: the v1.0 repo (Levels 1 to 3, results dated
2026-11-04) plus the follow-up added on branch site/live-dashboard.
Rubric: the questions a PhD committee would ask of an empirical
systems study. Each section says what the repo had, what this change
fixed, and what is still open, with the exact data or compute the
open part needs.

### Summary

The repo is an honest, small, fully reproducible engineering study.
Its strongest qualities are pre-labelled expectations, deterministic
runners, and limits written down in each README. Its weakest is
external validity: no language model is measured anywhere, and every
rate rests on single-digit counts from a designed set. This change
fixed what could be fixed with stdlib Python in seconds: uncertainty
intervals, a differential check against a reference validator, a
supplementary labelled set that exercises the coercion rule and
multi-defect records, a CI byte-for-byte reproduction gate, and a
second-language reproduction (the dashboard's JS ports must
reproduce every committed results file before the site builds).

### 1. Research question

Implicit but clear from SPEC.md and the Deep README: can a bounded,
rule-based repair loop raise the share of schema-valid records
without introducing false values, and how often does a "healed"
record state something the source did not? The question is
well-posed for the designed set. It is not yet a question about
model output, because no model output enters the loop.

### 2. Hypotheses

The evaluation sets act as pre-registered predictions: every
document's expected outcome was labelled before the run, and the
runners exit non-zero on any mismatch. What was missing was an
explicit falsifiable claim about the rules. The supplementary set
(level-3-deep/supplement.json) adds testable predictions that the
v1.0 set could not reach: that numeric strings are recovered
exactly, that "4.5" never becomes an integer, that a boolean is
never coerced, that one unrepairable defect keeps a multi-defect
record rejected, and that coerce-then-clamp needs two repair rounds.
The labels were committed (commit "Level 3: label a supplementary
set ...") before the runner existed. All 10 predictions held.

### 3. Method

Strong: deterministic extractors and rules, the Level 1 validator
reused unchanged by Levels 2 and 3, labelled expectations, runners
that compare against them, deterministic results files.

Weak, and now partly addressed: the v1.0 benchmark cannot exercise
coerce_numeric_string at all. This review found why: the Level 2
extractor parses numeric tokens with the same float() and int() the
coercion rule uses, so a string that would coerce is already a
number before it reaches the loop. The rule is reachable only for
records produced elsewhere (for example a model's JSON output). The
supplementary set feeds such records directly, and the coercion rule
applied 7 times (results_supplement.json).

Open: the inputs are still designed by the author. See section 7.

### 4. Baselines and comparisons

Before: none. NOVELTY.md's prior-art table reads "NO MEASUREMENT
YET".

Fixed here: a differential test (tests/test_learn_differential.py)
runs the jsonschema package (Draft 2020-12) on the same inputs as
the subset validator. They agree on all 9 parseable Level 1 case
arguments and all 16 Level 2 candidate records. One disagreement is
by design and is pinned as a test: the subset rejects 60.0 for an
integer field, the standard accepts it. The rule ablation on the
dashboard (rules toggled, max_rounds varied) is a within-system
comparison on the recorded set: with clamp_to_range off, the
recorded set heals 1 of 8 with 0 silent failures, which is the
trade-off the Deep README describes in words. It is labelled as a
what-if on the recorded set, not a new benchmark.

Open, needs compute: comparison with other repair strategies
(re-asking the model with the validator errors, constrained decoding
such as grammar-guided generation, json-repair style text fixes)
needs a model generating the outputs. Exact need: a free local
instruct model served on a local GPU (no paid API), the 16 documents plus a larger set run through
it with and without each strategy, and the outputs labelled the same
way (ROADMAP v1.1 item 5). That is a GPU job and a labelling job, so
it is out of scope for this change by rule. A json-repair style
baseline on its own does not fit this benchmark: those tools fix
malformed JSON text, and every input here is already parsed.

### 5. Statistics and uncertainty

Before: point estimates only (0.375, 0.667, 1.000) on n = 8, 3 and
8.

Fixed here: level-3-deep/uncertainty.py writes Wilson 95% score
intervals for every rate to uncertainty.json, with unit tests that
check them against hand-worked values, and CI regenerates and diffs
the file. Repair rate 3 of 8: 0.137 to 0.694. Silent failure rate
2 of 3: 0.208 to 0.939. Validation catch rate 8 of 8: 0.676 to 1.000.
Supplementary set: repair 6 of 10, 0.313 to 0.832; silent 2 of 6,
0.097 to 0.700. The dashboard shows each interval next to its point
estimate and recomputes it live in the rule what-if.

Caveat stated here, not hidden: the 40 extracted fields come from 8
documents and are not independent, so the 0.912 lower bound on
extraction accuracy is optimistic. The defensible unit is the
document.

Open, needs data: intervals this wide cannot separate rule sets.
Narrowing the repair-rate interval to roughly plus or minus 0.1
needs on the order of 100 rejected records per condition, labelled
before the run. That is a labelling effort, not compute; generating
them from the same author's templates would shrink the interval
without fixing the validity threat in section 7.

### 6. Reproducibility

Before: stdlib only, deterministic runners, sha256 of results
recorded in the Deep README, CI running every runner on Python 3.11
and 3.12. Gap: CI re-ran the runners but did not fail if their
output differed from the committed files.

Fixed here: CI now regenerates results_build.json, results_deep.json,
results_supplement.json and uncertainty.json and fails on any byte
difference (git diff --exit-code). Independently, the dashboard
build (site/src/lab.check.mjs) re-implements the validator,
dispatcher, extractors and heal loop in JavaScript and asserts that
every record, error list (messages included, so Python float
formatting is matched), repair log, status, round count and summary
equals the committed Python results. A second implementation in a
second language reproducing the results is stronger evidence than
re-running the first.

### 7. Threats to validity

Internal: rules and labels are deterministic and pinned by tests,
so the internal threats are small. Construct: "silent failure" is
defined against hand-labelled truthful records; a clamp has no
truthful record by construction, so every clamp counts as silent.
That is a defensible definition and the README states it.

External, the main threat: the documents are synthetic, one defect
each in v1.0, designed by the same author who wrote the rules and
the labels. The rates describe these rules on this set, not
self-healing in general, and not model behaviour. The dashboard and
README now say so next to the numbers.

Open, needs a person: an independent second labeller for the
truthful records and an agreement measure (for example Cohen's
kappa on the expect_healed and truthful-record labels). No compute
needed; it needs someone other than the author.

### 8. Related work

Moved to PROPOSAL.md, section Prior work.

### 9. Limitations

Each level README has a "Limits, stated plainly" section and the
Deep README has a failure-mode list; both are specific and match the
evidence. The dashboard quotes them verbatim at build time rather
than paraphrasing. One addition from this review: the coercion rule
is unreachable through the Level 2 pipeline (section 3).

Scope limits that are not rigor gaps: no nested or array repairs,
and the validator is a teaching subset (no $ref, oneOf or anyOf,
format, uniqueItems). Extending either changes the measured system;
under the repo's standing v1.1 rules that needs its own labelled set
and a before-and-after measurement, so it is left to the backlog.

### What changed in this review, file by file

- level-3-deep/uncertainty.py, uncertainty.json,
  tests/test_deep_uncertainty.py: Wilson intervals.
- tests/test_learn_differential.py: agreement with jsonschema
  (test-only dependency, installed in CI, skipped where absent).
- level-3-deep/supplement.json (labels, committed first),
  run_supplement.py, results_supplement.json,
  tests/test_deep_supplement.py: the supplementary set.
- .github/workflows/ci.yml: runs the new scripts and fails on any
  difference in the committed results files.
- site/: the live dashboard, with the JS ports and the parity check
  that runs inside npm run build.

## Open backlog

1. Numeric-string defect set: add malformed documents whose
   typed fields carry numeric strings (a total of "249.50"
   left as text, a stock of "140"), so the coercion rule is
   measured in the benchmark, not only in unit tests, and
   re-baseline the repair rate on the enlarged set.
2. Multi-defect documents: documents carrying two or more
   defects at once, including one safe and one unrepairable
   defect in the same record, to measure partial repair
   behaviour and confirm a record with any unrepairable error
   still ends rejected with a complete log.
3. Nested and array repairs: extend the loop beyond flat top
   level fields to nested object paths and array items (for
   example an attendees entry of the wrong type), with the
   same named-rule and logging discipline.
4. Caller contract for flagged heals: a small consumer example
   that routes healed_flagged records to a review queue and
   healed_clean records onward, so the clamp flag is exercised
   end to end instead of only reported.
5. Real model output set: run the loop over genuine model
   extractions (a free local route only, no spend and no new
   credential created by this project on its own), labelled
   the same way, and report how the repair and silent failure
   rates move off the designed set.
6. Paper candidate: the self-healing parse reliability note
   named in SPEC.md (repair rate, silent failure rate, one
   table) is recorded in the publications tracker. Submission
   itself is Jesun's tap and is not part of any automated run.

(From ROADMAP.md, 2026-11-04. Items 1 and 2 were measured on
2026-11-07 by the supplementary set; the rest are not done and not
claimed.)

## Conclusion

On the designed sets, the validator stops every designed defect at its
field, and safe self-healing is narrow: the only clean heals are
dropping an extra field and, on the supplementary set, coercing a
cleanly parsing numeric string. Every clamp produced a silent failure,
which argues against routine clamping. None of this is yet a claim
about language-model output; that needs the backlog's real model
output set under a locked proposal.

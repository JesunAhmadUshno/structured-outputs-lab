# Tutorial: P14 structured-outputs-lab, course module

Module: P14-structured-outputs-lab
By Jesun Ahmad Ushno
Date: 2026-11-04
License for this tutorial: CC BY 4.0. Code in the repo: Apache-2.0.

## What you will do

You will clone the structured-outputs-lab repo, run all three
levels, run the test suite for each level, and read your own
results against the recorded v1.0 numbers. Every command below
exists in the repo as shipped at v1.0 and was run by the author of
this module on 2026-11-04 to verify it. The project needs
Python 3.12 and uses the standard library only. No model, no API,
and no credential are needed. Commands are written with python3,
which is the Python 3 command on the machine where they were
verified.

All recorded numbers in this module come from synthetic designed
sets. They prove the validate-then-dispatch gate, the extraction
pipeline mechanism, and the self-healing loop discipline. They do
not prove production quality on real documents or real model
output.

## Step 0: Clone and enter the repo

```text
git clone https://github.com/JesunAhmadUshno/structured-outputs-lab.git
cd structured-outputs-lab
```

## Step 1: Level 1, Learn, validate then dispatch

Read level-1-learn/README.md first. It explains the strict JSON
Schema subset validator (types, required fields, enums, nested
objects, arrays, string and number constraints, and strict mode
with additionalProperties False) and the dispatcher around three
example functions, each with a strict schema. One subtle rule to
notice: a JSON true is never accepted as a number or an integer,
even though Python bool subclasses int.

Run the Learn case set:

```text
python3 level-1-learn/run_cases.py
```

Run the Learn tests:

```text
python3 -m unittest discover -s tests -p "test_learn*.py" -v
```

Read your results:

- Expected summary: 10 of 10 cases matched expectation; 4 calls
  dispatched to functions, 6 rejected before dispatch.
- Expected call counts: get_weather 2, create_calendar_event 1,
  score_keywords 1.
- Expected rejection paths, in case order: $.unit, $.date, $.room,
  $.date, $.keywords[1], and $ for the invalid JSON case.
- Expected tests: 16 tests, all passing.

## Step 2: Level 2, Build, extraction with validation on every output

Read level-2-build/README.md and level-2-build/BUILD-SPEC.md. The
pipeline holds 16 synthetic documents in 3 types (invoice, meeting
note, product listing), one deterministic regex extractor per
type, one strict schema per type, validation of every extracted
record with the Learn validator reused unchanged, and routing of
failures to a rejection list with the full validator errors. A
token that does not parse cleanly stays a string, so the validator
reports the type error instead of the extractor hiding it.

Run the Build pipeline:

```text
python3 level-2-build/run_build.py
```

Run the Build tests:

```text
python3 -m unittest discover -s tests -p "test_build*.py" -v
```

Read your results:

- Expected summary: 16 of 16 documents matched expectation; 8
  accepted, 8 rejected.
- Expected extraction accuracy on accepted docs: 40 of 40 fields
  correct (1.000).
- Expected validation catch rate on malformed docs: 8 of 8 caught
  (1.000). False accepts: 0.
- The runner writes level-2-build/results_build.json.
- Expected tests: 18 Build tests, all passing, 34 in total with
  Learn.

## Step 3: Level 3, Deep, the self-healing parse loop

Read level-3-deep/README.md and level-3-deep/DEEP-SPEC.md. This
is a compressed Deep: a self-healing parse loop over the 8 Build
rejections, with named deterministic repair rules
(drop_additional_field, coerce_numeric_string, clamp_to_range),
every attempt logged, missing fields never invented, invalid enum
values never guessed, and the loop bounded at 3 rounds. The rest
of the v2 Deep scope is the v1.1 backlog in ROADMAP.md at the repo
root.

Run the Deep healing loop:

```text
python3 level-3-deep/run_deep.py
```

Run the Deep tests:

```text
python3 -m unittest discover -s tests -p "test_deep*.py" -v
```

Read your results:

- Expected summary: 8 of 8 rejected documents matched the
  labelled outcome; 3 healed (1 clean, 2 flagged), 5 still
  rejected.
- Expected repair rate: 3 of 8 (0.375).
- Expected silent failure rate: 2 of 3 healed (0.667). Both
  flagged heals are clamps whose healed values differ from the
  values the documents state.
- Expected valid records altered: 0 of 8 Build-accepted records.
- The runner writes level-3-deep/results_deep.json.
- Expected tests: 21 Deep tests, all passing, 55 in total with
  Learn and Build.

## Step 4: Run the full test suite

```text
python3 -m unittest discover -s tests -v
```

Expected: 55 tests in total (16 Learn, 18 Build, 21 Deep), all
passing.

## Step 5: Check your understanding

1. Why is a JSON true never accepted as a number at Learn?
   (Answer: Python bool subclasses int, so a naive type check
   would pass a boolean where a number belongs. The validator
   checks bool first, so the shape stays strict.)
2. At Build, why does a non-numeric total stay a string in the
   extracted record instead of being dropped or coerced? (Answer:
   so the validator reports the type error at its path. The
   extractor must not hide a defect the validation gate exists to
   catch.)
3. At Deep, the repair rate is 0.375 and the silent failure rate
   is 0.667. Why is the second number not a counting defect?
   (Answer: it is the labelled finding. Both out-of-range heals
   are clamps, and a clamp fixes the shape while changing the
   fact, so under the pre-labelled definition each clamp counts
   as a silent failure, flagged in the log and on the record.)

## Limits to keep with the numbers

- Synthetic designed sets only, at every level.
- No language model is used anywhere in this repo. Extractors are
  deterministic and regex based over one fixed line format per
  type.
- The validator is a strict subset of JSON Schema, not the full
  specification.
- Validation proves shape, not truth, and the repair rates are
  properties of this defect set and these rules, not of
  self-healing in general.

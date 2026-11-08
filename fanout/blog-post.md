# Answers in Shape: Validated Extraction and a Self-Healing Parse Loop, Measured Honestly

By Jesun Ahmad Ushno
Date: 2026-11-04
Status: DRAFT, written fan-out for P14 structured-outputs-lab v1.0. Not posted.

## The problem

A language model produces text. An application needs data it can
trust: a field that is present, typed, in range, and free of
surprises. If an invalid function call is dispatched, the error
happens downstream where it is harder to trace. If an extracted
record is accepted with a missing or out-of-range field, the shape
looks fine while the fact is wrong. And if a system repairs a bad
record by guessing, its repair rate can look better while the data
gets worse.

This project, P14 in Roadmap v3, builds the defence in the open,
one level at a time: a strict schema validator with a
validate-then-dispatch gate for function calling, then a document
extraction pipeline that validates every output, then a
self-healing parse loop that attempts repairs only under named
rules, logs every attempt, and never invents data. All code runs
with the Python 3.12 standard library only. No language model, no
API, and no credential are used anywhere in this repo, and nothing
here claims otherwise. The extractors are deterministic and regex
based, and the case and document sets are synthetic and designed.

Repository: https://github.com/JesunAhmadUshno/structured-outputs-lab

## Past, present, future (the dossier, condensed)

Past: schema libraries and JSON mode documentation already exist.
The prior art and the problem history are recorded in DOSSIER.md
and NOVELTY.md in the repo. The novelty claim there stays marked
PROPOSED. This post makes no novelty claim beyond the measured
work below.

Present: v1.0 closes three levels on 2026-11-04. Learn built the
validator and dispatcher small and checkable by eye. Build ran a
document extraction pipeline over 16 synthetic documents in 3
types and routed every failure to a rejection list with validator
error paths. Compressed Deep built the SPEC Deep capability: a
self-healing parse loop over the 8 Build rejections, with named
repair rules, a full repair log, and a pre-labelled expected
outcome set.

Future: the rest of the v2 Deep scope is named in ROADMAP.md in
the repo as the v1.1 backlog. It includes a numeric-string defect
set that measures the coercion rule in the benchmark, multi-defect
documents, nested and array repairs, a caller contract for flagged
heals, and a real model output set. None of that is done, and none
of it is claimed here.

## Main results claim

At v1.0, on synthetic sets only: Learn passed 16 tests with 10 of 10 cases matched, 4 calls dispatched (get_weather 2, create_calendar_event 1, score_keywords 1) and 6 rejected before dispatch at their named error paths ($.unit, $.date twice, $.room, $.keywords[1], and $); Build passed 18 tests (34 tests in total) with 16 of 16 documents matched, 8 accepted and 8 rejected, extraction accuracy 1.000 (40 of 40 fields on the expected-accept documents), validation catch rate 1.000 (8 of 8 malformed documents rejected at their designed first error paths), and 0 false accepts; compressed Deep passed 21 tests (55 tests in total) over the 8 Build rejections, with 8 of 8 documents matched to the labelled outcome, 3 healed and 5 still rejected, repair rate 0.375 (3 of 8), silent failure rate 0.667 (2 of 3 healed are flagged value-changing clamps), and 0 of 8 Build-accepted records altered.

Every number in that claim comes from a run recorded in the level
READMEs in the repo, on synthetic designed sets. Read the limits
section below before quoting any of it.

## Results by level

### Level 1, Learn (release v0.1)

The case set holds 10 model-style function calls against strict
schemas for three example functions (get_weather,
create_calendar_event, score_keywords). Each rejection case was
hand built so it has one named cause.

| Measure | Result |
| --- | --- |
| Cases | 10 of 10 matched expectation |
| Dispatched | 4 (get_weather 2, create_calendar_event 1, score_keywords 1) |
| Rejected before dispatch | 6, each at its designed error path ($.unit, $.date twice, $.room, $.keywords[1], $) |
| Tests | 16 |

Read honestly: this is a designed teaching set, not a model
benchmark. No real model output was scored at this level. The
numbers prove the gate logic: valid calls pass, and each invalid
call is stopped at the field the case designed it to fail on.

### Level 2, Build (release v0.5)

The corpus holds 16 synthetic documents in 3 types (invoice,
meeting note, product listing). Eight are well formed. Eight are
deliberately malformed, each with exactly one designed defect:
missing field (2), wrong type (2), extra field (1), out-of-range
value (2), invalid enum value (1). Every extracted record is
validated with the Learn validator, reused unchanged.

| Measure | Result |
| --- | --- |
| Documents | 16 of 16 matched expectation |
| Split | 8 accepted, 8 rejected |
| Extraction accuracy | 1.000 (40 of 40 fields on expected-accept documents) |
| Validation catch rate | 1.000 (8 of 8 malformed documents) |
| False accepts | 0 |
| Tests | 18 Build, 34 in total with Learn |

Read honestly: 1.000 on both rates over 16 short synthetic
documents proves the pipeline mechanism end to end. It does not
prove extraction on real documents, which vary in layout and
carry noise this corpus never shows.

### Level 3, Deep, compressed (release v1.0)

The loop takes the 8 Build rejections and attempts repairs from
the validator errors under named deterministic rules only:
drop_additional_field (safe), coerce_numeric_string (safe,
representation only), and clamp_to_range (always flagged
value-changing). Missing required fields and invalid enum values
have no rule: a missing field is never invented and an enum value
is never guessed. The loop is bounded at 3 rounds, and every
attempt is logged with before and after values.

| Measure | Result |
| --- | --- |
| Documents matched | 8 of 8 matched the labelled outcome |
| Healed | 3 (1 clean heal from dropping an additional field, 2 flagged clamps) |
| Still rejected | 5 |
| Repair rate | 0.375 (3 of 8) |
| Silent failure rate | 0.667 (2 of 3 healed) |
| Build-accepted records altered | 0 of 8 |
| Tests | 21 Deep, 55 in total with Learn and Build |

The finding of this level is narrow by design. The only clean
heal is the extra field drop. Both out-of-range heals are clamps,
and both count as silent failures under the pre-labelled
definition: a clamped invoice total of 100000 is a valid shape
carrying a false fact, because the document stated 250000. The
loop makes that visible instead of hiding it: the clamp is flagged
in the log, on the record status, and in this rate. The coercion
rule heals nothing in this set, because both wrong-type documents
carry strings that do not parse ("FREE", "many"); the rule is
proven by unit tests, not by this benchmark, and no number here
claims otherwise.

## Honest limits

- Synthetic designed sets only. Learn uses 10 hand built cases;
  Build uses 16 synthetic documents; Deep reuses the same 8 Build
  rejections, one defect per document. No claim about real model
  output, real documents, scale, or latency is made or implied.
- No language model is involved at any level in v1.0. The
  extractors are deterministic regex and rule based over one fixed
  line format per type.
- The validator is a strict subset of JSON Schema. It has no $ref,
  no allOf or anyOf or oneOf, no format keyword, and no conditional
  schemas.
- Validation proves shape, not truth. An invoice whose total is in
  range but wrong for its items passes. Semantic checks belong to
  the caller.
- The repair and silent failure rates are properties of this
  designed defect set and these named rules, not of self-healing
  in general.
- Clamping is included as a flagged rule so its cost is measured,
  not because clamping financial or duration values is good
  practice. Every clamp in this set produced a silent failure.
- Compressed Deep is not the full v2 Deep scope. The remainder is
  the named v1.1 backlog in ROADMAP.md.
- The runs executed on the Muse VM, not the assigned BlackBoxV3
  node.

## Where to go next

- Tutorial: fanout/tutorial.md in the repo, a step-by-step module
  that runs all three levels and the full test suite.
- Releases: v0.1 (Learn), v0.5 (Build), v1.0 (Learn, Build,
  compressed Deep) on the GitHub repo linked above.
- Book chapter: "Answers In Shape" per SPEC.md, drafted as part of
  the fan-out set.
- License: code Apache-2.0, tutorials CC BY 4.0.

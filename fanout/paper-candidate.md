# Paper candidate brief: self-healing parse reliability note

Tracker row: CANDIDATE row for P14 (publications pipeline tracker)
Project: P14 structured-outputs-lab
Status: CANDIDATE, brief written 2026-11-04
Submission note: submission is Jesun's tap. Nothing is submitted by
this brief, and no venue has been contacted.

## Working title

Repair rate is not reliability: a self-healing parse loop with
named rules, full repair logs, and a measured silent failure rate

## Abstract draft

Based only on the measured v1.0 results recorded in the repo.
Numbers below are from synthetic designed sets and are stated as
such.

Structured output pipelines usually report how many rejected
records a repair step recovers. This work argues that the recovery
count alone is the wrong headline, and measures a self-healing
parse loop by both its repair rate and its silent failure rate.
The loop sits on a strict schema validation stack built in two
earlier levels. At Learn level, a strict JSON Schema subset
validator with a validate-then-dispatch gate passed 16 unit tests
and matched 10 of 10 designed function calling cases: 4 valid
calls dispatched and 6 invalid calls rejected before dispatch at
their named error paths. At Build level, a document extraction
pipeline over 16 synthetic documents in 3 types (invoice, meeting
note, product listing), with deterministic extractors and one
strict schema per type, matched 16 of 16 documents: 8 accepted and
8 rejected, extraction accuracy 1.000 (40 of 40 fields on the
expected-accept documents), validation catch rate 1.000 (8 of 8
malformed documents), and 0 false accepts, with 18 unit tests (34
in total). At Deep level, the loop attempted repairs on the 8
Build rejections under named deterministic rules only
(drop_additional_field, coerce_numeric_string, clamp_to_range),
with every attempt logged, missing fields never invented, invalid
enum values never guessed, and re-validation after each round for
at most 3 rounds. Against an expected healed outcome set labelled
before the run, 8 of 8 documents matched: 3 healed and 5 still
rejected, for a repair rate of 0.375 (3 of 8). Of the 3 healed
records, 1 was a clean heal (dropping an additional field) and 2
were flagged value-changing clamps whose healed values differ
from the values the documents state, giving a silent failure rate
of 0.667 (2 of 3 healed) under the pre-labelled definition. No
Build-accepted record was altered (0 of 8). The stack ships with
55 unit tests. The sets are synthetic and designed, the defect
classes are one per document, the coercion rule heals nothing in
the benchmark set and is proven only by unit tests, and the paper
claims the two-rate reporting discipline and the measured result
on these sets, not self-healing performance in general.

## Method outline

1. Validation stack: a strict JSON Schema subset validator (types,
   required fields, enums, nested objects, arrays, string and
   number constraints, strict mode) reused unchanged at every
   level, so a repair is judged by the same gate that rejected the
   record.
2. Extraction pipeline: deterministic regex and rule based
   extractors, one per document type, over a labelled 16-document
   synthetic corpus. A token that does not parse cleanly stays a
   string, so type defects reach the validator instead of being
   hidden by the extractor.
3. Repair rules, the complete named set: drop_additional_field
   removes an extra field (safe); coerce_numeric_string replaces a
   string with the number or integer it parses cleanly to, and
   nothing else (safe, representation only); clamp_to_range
   replaces an out-of-range value with the nearest schema bound
   and is always flagged value-changing. Missing required fields
   and invalid enum values have no rule, by design.
4. Loop discipline: one repair per current error, then
   re-validation, for at most 3 rounds. The input record is never
   mutated. Every attempt, applied or unrepairable, is logged with
   document id, round, error path, error code, rule name, before
   value, after value, a value-changing flag, and outcome. A healed
   record always carries its full repair log.
5. Scoring: the expected healed outcome set is labelled before the
   run. A healed record is correct only when a truthful healed
   record exists in the labelled set and the healed record equals
   it. A flagged clamp has no truthful healed record, so it counts
   as a silent failure. Repair rate is healed divided by attempted;
   silent failure rate is silent failures divided by healed.

## Results table

Measured 2026-11-04, synthetic designed sets only, from the level
READMEs in the repo.

| Level | Set | Headline result | Rates | Tests |
| --- | --- | --- | --- | --- |
| Learn | 10 designed cases | 10 of 10 matched; 4 dispatched, 6 rejected at named paths | n/a | 16 |
| Build | 16 documents, 3 types | 16 of 16 matched; 8 accepted, 8 rejected | Extraction 1.000 (40 of 40), catch 1.000 (8 of 8), false accepts 0 | 18 (34 total) |
| Deep, by class | 8 rejections: missing 2, wrong type 2, extra field 1, out of range 2, bad enum 1 | Healed: extra field 1 of 1, out of range 2 of 2 (both flagged); all other classes 0 | Repair rate 0.375 (3 of 8) | 21 Deep (55 total) |
| Deep, quality of heals | 3 healed records | 1 clean heal, 2 flagged clamps | Silent failure rate 0.667 (2 of 3); accepted records altered 0 of 8 | 21 Deep (55 total) |

Named case: the clamped invoice. The document states a total of
250000, outside the schema maximum of 100000. The loop clamps it
to 100000 and the record then validates. The paper must state this
as the central caution: the shape is fixed, the fact is changed,
and only the flag, the log, and the silent failure count keep that
visible.

## Venue class note

Per SPEC.md, the paper angle for P14 is a self-healing parse
reliability note (repair rate, silent failure rate, one table).
Venue class is a workshop or conference in NLP, LLM systems, or
software reliability, per the publications pipeline tracker rules.
One venue at a time. No venue is named as submitted, accepted, or
contacted in this brief. Fees, if any, arise only after acceptance
and remain Jesun's call under the free-only rule.

## Limits the paper must carry

- Synthetic designed sets only (10 cases; 16 documents; the same 8
  rejections at Deep). No real model output, no real documents, no
  scale or latency claim.
- One defect per malformed document. Real rejected output carries
  several defects at once, and partial repair behaviour on
  multi-defect records is v1.1 backlog, not a result.
- The coercion rule heals nothing in the benchmark set, because
  both wrong-type documents carry strings that do not parse
  ("FREE", "many"). It is proven by unit tests only, and the paper
  must not present it as benchmark measured.
- Repairs work on top level fields of flat records. Nested paths,
  arrays of objects, and cross-field repairs are not attempted.
- Clamping is measured so its cost is visible, not endorsed. On
  this set every clamp produced a silent failure.
- Compressed Deep only. The v1.1 backlog (numeric-string defect
  set, multi-defect documents, nested and array repairs, caller
  contract for flagged heals, real model output set) is future
  work, named in ROADMAP.md in the repo.

## Submission gate

Submission is Jesun's tap and nothing is submitted. This brief is
the candidate only. The tracker row stands at CANDIDATE for P14 in
the publications pipeline tracker.

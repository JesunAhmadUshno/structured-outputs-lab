# Level 3, Deep: structured-outputs-lab

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH, Sprint 1 of the
December Compression Protocol, compressed Deep). Evidence: the
code in this folder, 21 Deep unit tests in
tests/test_deep_healing.py (55 tests total with Learn and
Build), and the measured loop run recorded below and in
results_deep.json, written by the runner. Spec for this level:
DEEP-SPEC.md in this folder. The rest of the v2 Deep scope is
the v1.1 backlog in the repo root ROADMAP.md.

## What was built

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

## Run it

```text
python level-3-deep/run_deep.py
python -m unittest discover -s tests -p "test_deep*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

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

## Limits, stated plainly

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

## Next

The v1.1 backlog in the repo root ROADMAP.md: nested and
array repairs, a numeric-string-rich defect set that measures
the coercion rule in the benchmark, multi-defect documents,
and the paper candidate (a self-healing parse reliability
note) recorded in the publications tracker.

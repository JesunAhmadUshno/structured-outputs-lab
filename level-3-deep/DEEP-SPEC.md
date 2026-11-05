# Deep Spec: structured-outputs-lab Level 3 (compressed Deep)

## Objective
Close Deep per SPEC.md acceptance under the December Compression
Protocol: the single hardest capability in the SPEC, built,
tested, benchmarked, with the failure modes written. That
capability is a self-healing parse loop with every repair logged:
the rejected records from Level 2 Build are repaired from their
validator errors, under named deterministic rules, and the result
is measured for repair rate and silent failure rate.

Input set: the Build rejection list, the 8 malformed documents in
level-2-build/corpus.py (ids d09 to d16), extracted and rejected
by the Level 2 pipeline exactly as Build left them. No other
documents enter the benchmark. Repair rules are additionally
unit-tested on hand-built records in tests, never in the
benchmark numbers.

## Repair rules (the complete named set)
A repair is attempted only when a rule below names it. Every
attempt, applied or not, is logged with doc id, round, error
path, error code, rule name, before value, after value, a
value-changing flag, and outcome.

1. drop_additional_field (safe, value-preserving for the kept
   fields): an error with code additional removes the extra
   field. The dropped value is recorded in the log.
2. coerce_numeric_string (safe, representation only): an error
   with code type where the value is a string and the field
   schema type is number or integer, and the string parses
   cleanly to that type (float for number, int for integer, so
   "4.5" never becomes an integer), replaces the string with the
   parsed number. A string that does not parse cleanly (for
   example "FREE" or "many") is unrepairable under this rule.
3. clamp_to_range (value-changing, always flagged): an error
   with code minimum, maximum, exclusive_minimum, or
   exclusive_maximum replaces the value with the nearest schema
   bound (for exclusive bounds on integers, one step inside the
   bound; on numbers, 0.01 inside). The log entry and the healed
   record both carry the value-changing flag. A clamped record
   is counted as healed_flagged, never as a clean heal, because
   clamping changes what the document said.
4. No rule (unrepairable): code required (a missing field is
   never invented), code enum (an invalid enum value is never
   mapped to a guessed valid one, and no default is named in
   these schemas), code pattern, min_length, max_length,
   min_items, max_items, and any type error the coercion rule
   does not cover. The attempt is logged with outcome
   unrepairable and the record stays rejected.

Loop: validate, attempt one repair per current error, then
re-validate. At most 3 rounds. A record that still fails after
the loop stays rejected with its final error list and its full
repair log. A record that passes is healed and must carry its
full repair log; there is no path where a repaired record passes
without a log. A record that was already valid is returned
unchanged with an empty log and status already_valid.

## Measurement (labelled before the run)
The expected healed outcome set (evaluation_deep.json in this
folder) is authored before the benchmark run, in the style of
the Build evaluation set. Per rejected document it states the
defect class, whether a heal is expected, whether a flagged
value-changing heal is expected, the true record (the record the
document actually carries, as extracted at Build), and, where a
truthful healed record exists, that record exactly.

- attempted: rejected records fed to the loop (8).
- healed: records that pass validation after repairs. Reported
  split into healed clean and healed flagged.
- repair rate: healed divided by attempted.
- silent failure: a healed record that is wrong. A healed
  record is correct only when a truthful healed record exists
  in the labelled set and the healed record equals it. A
  flagged clamp has no truthful healed record (the true value
  is out of range by construction), so a clamped heal counts
  as a silent failure: the shape is fixed, the fact is changed.
  This definition is chosen before the run and is not adjusted
  after it.
- silent failure rate: silent failures divided by healed.
- per-defect-class outcomes: attempted, healed, and silent
  failures for missing, wrong_type, extra_field, out_of_range,
  and bad_enum.
- valid record safety: every Build-accepted record is also fed
  to the loop; the count altered must be 0.

## Assumptions
- Python standard library only. No external model, API,
  credential, or spend. No network.
- The schemas and the Learn validator are reused unchanged.
  The loop repairs records against the Level 2 schemas.
- The corpus is synthetic and labelled synthetic. The numbers
  measure the repair mechanism on 8 designed defects, not
  repair quality on real model output.

## Commands
- Test: python -m unittest discover -s tests -p "test_deep*.py" -v
- Run: python level-3-deep/run_deep.py
- Full: python -m unittest discover -s tests -v

## Boundaries
- Always: stdlib only, deterministic rules, every repair logged,
  clamped heals flagged as value-changing, results recorded
  exactly as measured, unrepairable defects left rejected.
- Never: invent a missing field value, guess an enum mapping,
  silently clamp, silently coerce a string that does not parse
  cleanly, pass a healed record without its repair log, alter a
  record that already validates, or claim a heal the log cannot
  show.

## Success criteria
- Each of the 8 rejected records ends in the outcome the
  labelled set expects (healed or still rejected), and the one
  truthful healed record (the extra field case) matches exactly.
- Repair rate, silent failure rate, and per-defect-class
  outcomes are printed by the runner and stored in
  results_deep.json.
- No Build-accepted record is altered by the loop.
- The runner is deterministic: two runs write identical
  results_deep.json.
- At least 12 Deep tests pass; Learn and Build tests still pass.

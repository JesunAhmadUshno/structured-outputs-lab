# ROADMAP: structured-outputs-lab v1.1 backlog

v1.0 (2026-11-04) closes Learn, Build, and compressed Deep.
Compressed Deep delivered the single hardest capability in the
SPEC: a self-healing parse loop with every repair logged,
measured on the 8 Build rejections for repair rate (0.375) and
silent failure rate (0.667). The items below are the rest of
the v2 Deep scope, named here as the v1.1 backlog. None of
them is done, and none is claimed.

## v1.1 backlog

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

## Standing rules for v1.1 work

- The Build pipeline and the Learn validator stay unchanged
  in behaviour unless a change is itself measured before and
  after on the Deep set.
- No new repair rule ships without a name, a log format, a
  unit test per rule, and a labelled expectation in the Deep
  evaluation set before the run that measures it.
- Every new number in a README comes from a run executed in
  that cycle. Nothing is carried forward as if it were
  freshly measured.

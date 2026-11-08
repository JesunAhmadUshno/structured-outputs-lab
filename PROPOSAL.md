# Proposal: structured-outputs-lab

Status: NOT LOCKED. Not pre-registered. Assembled on 2026-11-08, at
the move to the portfolio standard v2, from the plan files that existed
before: SPEC.md (the 2026-11-04 scaffold spec, commit 57ca279),
NOVELTY.md, DOSSIER.md, level-2-build/BUILD-SPEC.md and
level-3-deep/DEEP-SPEC.md. Their text is kept below as written.

Why it is not a lock: the scaffold spec came first, but it states a
scope, not hypotheses or pass lines. The Build and Deep specs and their
labelled expectation sets were committed in the same commits as the
results they score (6284881 and f3b490f), so git history cannot prove
they came before the runs. Only the supplementary-set labels
(level-3-deep/supplement.json, commit c266ed4) provably precede their
runner (commit 090b837). A confirmatory cycle needs a new proposal,
tagged before its run; until then the repo is capped at Functional
(portfolio METHOD section 7).

## Question

Can a bounded, rule-based repair loop raise the share of schema-valid
records without introducing false values, and how often does a
"healed" record state something the source did not?

(Implicit in SPEC.md and the Deep spec; worded this way by the
2026-11-07 review, REPORT.md.)

## Scope (SPEC.md, 2026-11-04)

Phase skill: spec-driven-development (house engineering pipeline).
Status: Wave 0 scaffold spec, from Roadmap v2 text and the v3 decision pack. Scope and acceptance criteria below are the v2 section text, kept as the source of truth until the project's wave opens its own spec pass.

Fleet node: BlackBoxV3. Wave: Wave 2.

### Project section text

structured-outputs-lab: KEEP

Subject: reliable LLM applications. v1 levels carry over: JSON mode and function calling with strict schemas; a document extraction pipeline with schema validation on every output; Deep adds a self-healing parse loop with every repair logged.
Fan-out: Book chapter "Answers In Shape". Paper angle: a self-healing parse reliability note (repair rate, silent failure rate, one table). Course module: P14-structured-outputs-lab.

### Acceptance criteria (scaffold level)

- Learn closes when the level-1-learn code runs, its README teaches the idea, and a fresh-eyes reader can follow it.
- Build closes when the system runs end to end, tests pass, and one benchmark or result table with method is in the README.
- Deep closes when the Deep scope in the section text is done, the failure modes are written, and the dossier is updated to ship state.
- No level closes on a claim. Evidence only: code, tests, numbers, links.

## Prior work

### From DOSSIER.md (v1, 2026-11-04)

Prior art for this project is named in NOVELTY.md (schema libraries (Pydantic class) and JSON mode docs). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

Built state, 2026-11-04: Level 1 Learn is done (strict schema validator and function-calling dispatcher, 16 tests, 10 of 10 cases matched). Level 2 Build is done the same day under the December Compression Protocol: a document extraction pipeline over a 16-document synthetic corpus in 3 types (invoice, meeting note, product listing), with deterministic regex extractors, one strict schema per type, every output validated with the Learn validator, and failures routed to a rejection list with validator error paths. Measured: extraction accuracy 1.000 (40 of 40 fields), validation catch rate 1.000 (8 of 8 malformed documents), 0 false accepts, 18 Build tests (34 total). Level 3 Deep is done the same day as compressed Deep, and the project is at v1.0 ship state: a self-healing parse loop over the 8 Build rejections, with deterministic named repair rules (drop additional field, coerce a cleanly parsing numeric string, flagged clamp to range), every repair attempt logged, missing fields never invented and invalid enum values never guessed, the loop bounded at 3 rounds. Measured on an expected healed outcome set labelled before the run: 8 of 8 documents matched the labelled outcome, 3 healed and 5 still rejected, repair rate 0.375 (1 clean heal, 2 flagged clamps), silent failure rate 0.667 (both clamped heals state values the documents did not), 0 of 8 Build-accepted records altered, 21 Deep tests (55 total). Full record: level-3-deep/README.md and level-3-deep/results_deep.json. The rest of the v2 Deep scope is the v1.1 backlog in ROADMAP.md.

Open problems and the project's next steps sit in the Deep level scope in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

### Comparison set named by the 2026-11-07 review

Before: DOSSIER.md and NOVELTY.md name "schema libraries (Pydantic
class) and JSON mode docs" with no dated sources.

Added here as the comparison set the next pass should read against,
without claiming any of their results:

- JSON Schema, Draft 2020-12 (json-schema.org): the standard the
  subset follows; the differential test measures agreement with it
  through the jsonschema package.
- Pydantic: typed validation with coercion ("lax mode"), the closest
  analogue to coerce_numeric_string.
- Willard and Louf, "Efficient Guided Generation for Large Language
  Models", arXiv:2307.09702 (2023): constrained decoding, which
  prevents schema errors at generation time instead of repairing
  them afterwards.
- Tam et al., "Let Me Speak Freely? A Study on the Impact of Format
  Restrictions on Performance of Large Language Models",
  arXiv:2408.02442 (2024): evidence that forcing output formats can
  change task quality, which bears on whether repair after the fact
  is preferable to constraint during generation.
- Re-ask loops (feeding validator errors back to the model, as
  libraries such as Instructor do): the model-side counterpart to
  this repo's rule-side repair.

Open: a dated literature pass, with the claim in NOVELTY.md
re-checked against it, is the owner's call under the repo's own
claim_check gate. No compute needed.

## Proposed novelty (NOVELTY.md, DRAFT)

Status: DRAFT, PROPOSED. Not verified. This text does not move into any public post, paper, or profile until the Jev claim_check gate passes on the exact text.

### Proposed claim

Against schema libraries (Pydantic class) and JSON mode docs: this project aims to differ in the way its SPEC.md section text defines (a from-zero or self-hosted build, measured in public, on a named home fleet, with the failure modes written down). The exact difference is stated at the project's wave, after the prior art is re-read.

### Prior art table

| Prior art | What it does | What this project does differently | Measured difference |
| --- | --- | --- | --- |
| schema libraries (Pydantic class) and JSON mode docs | See DOSSIER.md, Past | PROPOSED, see the claim above | NO MEASUREMENT YET |

### Honest size

If the novelty proves small, this file will say so and name the real value instead (a cleaner reproduction, a better benchmark, a first public dataset). No novelty is invented to fill this section.

## Design: extraction pipeline (BUILD-SPEC.md, committed with its results)

### Objective
Close Build per SPEC.md acceptance: the system runs end to end,
tests pass, and one benchmark table with method is in the README.
Build is a document extraction pipeline with schema validation on
every output:

1. A small synthetic document corpus (16 documents, 3 document
   types: invoice, meeting note, product listing), labelled
   synthetic in the corpus file and in every report. Documents are
   plain line-based text, the shape a scanned or emailed document
   takes after a plain text pass.
2. One deterministic extractor per type (regex and rule based,
   Python standard library only). Extractors are labelled honestly:
   no language model is involved at this level, and no file claims
   one is. Each extractor returns a candidate record.
3. One strict schema per type, validated with the Level 1 Learn
   validator (level-1-learn/schema_validate.py), reused unchanged.
   Strict means required fields, typed fields, ranges, patterns,
   enums where the type has them, and additionalProperties False.
4. A pipeline that extracts, validates every output, and routes
   each document to exactly one of two lists: accepted (record
   passed validation) or rejected (record plus the validator
   errors, with paths). An invalid extraction is never silently
   passed, coerced, or repaired at this level. Repair is Deep
   scope.
5. Deliberately malformed documents in the corpus (8 of 16) that
   must be rejected: missing field, wrong type, extra field,
   out-of-range value, and invalid enum value, so the rejection
   path is measured, not just claimed.

### Assumptions
- Python standard library only. No external model, API, credential,
  or spend. No network.
- The corpus and the evaluation set are synthetic and labelled as
  synthetic. They prove the extraction and validation mechanism end
  to end, not production extraction quality on real documents.
- The evaluation set (evaluation.json) states the expected outcome
  per document before the run: accept with expected key fields, or
  reject with the named first error path.

### Commands
- Test: python -m unittest discover -s tests -p "test_build*.py" -v
- Run: python level-2-build/run_build.py
- Full: python -m unittest discover -s tests -v

### Boundaries
- Always: stdlib only, deterministic extractors, the Learn
  validator reused unchanged, results recorded exactly as
  measured, malformed documents labelled as designed defects.
- Never: an external call, a new credential, a language model
  claim, a silent pass of an invalid record, a coercion that hides
  a type error (a non-numeric total stays a string so the validator
  rejects it), or a grade for a scaffold.

### Success criteria
- Each extractor returns the exact expected record for the valid
  documents of its type.
- Every malformed document is rejected at its designed first
  error path. False accepts are reported even if zero.
- Extraction accuracy on expected-accept documents (fields correct
  divided by fields total), validation catch rate on malformed
  documents, and the false accept count are printed by the runner
  and stored in results_build.json.
- The runner is deterministic: two runs write identical
  results_build.json.
- At least 12 Build tests pass; Learn tests still pass.

## Design: repair loop (DEEP-SPEC.md, committed with its results)

### Objective
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

### Repair rules (the complete named set)
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

### Measurement (labelled before the run)
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

### Assumptions
- Python standard library only. No external model, API,
  credential, or spend. No network.
- The schemas and the Learn validator are reused unchanged.
  The loop repairs records against the Level 2 schemas.
- The corpus is synthetic and labelled synthetic. The numbers
  measure the repair mechanism on 8 designed defects, not
  repair quality on real model output.

### Commands
- Test: python -m unittest discover -s tests -p "test_deep*.py" -v
- Run: python level-3-deep/run_deep.py
- Full: python -m unittest discover -s tests -v

### Boundaries
- Always: stdlib only, deterministic rules, every repair logged,
  clamped heals flagged as value-changing, results recorded
  exactly as measured, unrepairable defects left rejected.
- Never: invent a missing field value, guess an enum mapping,
  silently clamp, silently coerce a string that does not parse
  cleanly, pass a healed record without its repair log, alter a
  record that already validates, or claim a heal the log cannot
  show.

### Success criteria
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

## Standing rules for future work (ROADMAP.md)

- The Build pipeline and the Learn validator stay unchanged
  in behaviour unless a change is itself measured before and
  after on the Deep set.
- No new repair rule ships without a name, a log format, a
  unit test per rule, and a labelled expectation in the Deep
  evaluation set before the run that measures it.
- Every new number in a README comes from a run executed in
  that cycle. Nothing is carried forward as if it were
  freshly measured.

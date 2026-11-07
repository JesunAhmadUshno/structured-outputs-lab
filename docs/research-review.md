# Research review: structured-outputs-lab

Date: 2026-11-07. Scope: the v1.0 repo (Levels 1 to 3, results dated
2026-11-04) plus the follow-up added on branch site/live-dashboard.
Rubric: the questions a PhD committee would ask of an empirical
systems study. Each row says what the repo had, what this change
fixed, and what is still open, with the exact data or compute the
open part needs. Grades are this review's judgement, A (strong) to
D (missing); they are not results.

## Summary

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

| Criterion | Before | After | Open gap needs |
| --- | --- | --- | --- |
| Research question | B | B | nothing; see note |
| Hypotheses | C | B | nothing for this scope |
| Method | B | B+ | a non-designed input set (see external validity) |
| Baselines | D | C | a local model run (GPU), see below |
| Statistics and uncertainty | D | B | larger labelled sets (data, not compute) |
| Reproducibility | A- | A | nothing |
| Threats to validity | B | B+ | a second annotator |
| Related work | D | C | a dated literature pass by the owner |
| Limitations | A- | A- | nothing |

## 1. Research question (B)

Implicit but clear from SPEC.md and the Deep README: can a bounded,
rule-based repair loop raise the share of schema-valid records
without introducing false values, and how often does a "healed"
record state something the source did not? The question is
well-posed for the designed set. It is not yet a question about
model output, because no model output enters the loop.

## 2. Hypotheses (C to B)

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

## 3. Method (B to B+)

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

## 4. Baselines and comparisons (D to C)

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

## 5. Statistics and uncertainty (D to B)

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

## 6. Reproducibility (A- to A)

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

## 7. Threats to validity (B to B+)

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

## 8. Related work (D to C)

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

## 9. Limitations (A-)

Each level README has a "Limits, stated plainly" section and the
Deep README has a failure-mode list; both are specific and match the
evidence. The dashboard quotes them verbatim at build time rather
than paraphrasing. Two additions from this review: the coercion rule
is unreachable through the Level 2 pipeline (section 3), and the
self-assigned level and publicity grades in the repo are internal
scores, so the dashboard does not present them as findings.

Scope limits that are not rigor gaps: no nested or array repairs,
and the validator is a teaching subset (no $ref, oneOf or anyOf,
format, uniqueItems). Extending either changes the measured system;
under the repo's standing v1.1 rules that needs its own labelled set
and a before-and-after measurement, so it is left to the backlog.

## What changed in this review, file by file

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

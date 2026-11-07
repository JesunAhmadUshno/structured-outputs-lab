# structured-outputs-lab

Reliable LLM applications: strict schemas, validated extraction, a self-healing parse loop.

Live dashboard: https://jesunahmadushno.github.io/structured-outputs-lab/
(source in site/; in-browser ports of the validator, pipeline and repair
loop, rebuilt from the committed results and checked against them on
every build.)

Status: LEARN DONE, BUILD DONE, and DEEP DONE 2026-11-04
(ROADMAP-V3-BATCH, Sprint 1, compressed Deep). v1.0.
Level 1 code runs with 16 passing unit tests and one measured case
run (10 of 10 cases matched expectation, below). Level 2 code runs
with 18 Build unit tests and one measured pipeline run (16 of 16
documents matched expectation, below). Level 3 code runs with 21
Deep unit tests (55 total) and one measured loop run over the 8
Build rejections (8 of 8 matched the labelled outcome, repair rate
0.375, silent failure rate 0.667, below). The rest of the v2 Deep
scope is the v1.1 backlog in ROADMAP.md. The Wave 0 scaffold
claim is superseded by this line.
Project: P14. Fleet node: BlackBoxV3. Wave: Wave 2.

## Start here

1. Read SPEC.md for scope and acceptance criteria.
2. Read DOSSIER.md for the past, present, and future of this problem (v1).
3. Read NOVELTY.md for the proposed novelty (DRAFT, pending the Jev claim_check gate).
4. Start at level-1-learn/README.md, then level-2-build, then level-3-deep.

## Level map

- Level 1, Learn: the core idea, built small and clean, with a teaching path.
- Level 2, Build: a real working system other people can run.
- Level 3, Deep: benchmarks, optimization, evaluation, hard cases.

## Benchmarks

| Test | Result |
| --- | --- |
| Level 1 case run, 10 model-style function calls against strict schemas (method: level-1-learn/README.md), 2026-11-04 | 10 of 10 cases matched expectation: 4 valid calls dispatched (get_weather 2, create_calendar_event 1, score_keywords 1), 6 invalid calls rejected before dispatch, each at its designed error path ($.unit, $.date twice, $.room, $.keywords[1], $). Unit tests: 16 run, 16 passed. |
| Level 2 pipeline run, 16 synthetic documents in 3 types against strict schemas (method: level-2-build/README.md), 2026-11-04 | 16 of 16 documents matched expectation: 8 accepted, 8 rejected. Extraction accuracy 1.000 (40 of 40 fields on expected-accept documents), validation catch rate 1.000 (8 of 8 malformed documents rejected at their designed first error paths), 0 false accepts. Unit tests: 18 Build run, 18 passed; 34 total with Learn. |
| Level 3 healing run, the 8 Build rejections against a labelled expected healed outcome set (method: level-3-deep/README.md), 2026-11-04 | 8 of 8 documents matched the labelled outcome: 3 healed, 5 still rejected. Repair rate 0.375 (3 of 8: 1 clean heal from dropping an additional field, 2 flagged value-changing clamps), silent failure rate 0.667 (2 of 3 healed are clamps whose healed values differ from the values the documents state), 0 of 8 Build-accepted records altered. Unit tests: 21 Deep run, 21 passed; 55 total with Learn and Build. |

Follow-up, 2026-11-07 (does not change the v1.0 rows above):

| Test | Result |
| --- | --- |
| Uncertainty on every rate (level-3-deep/uncertainty.py, writes uncertainty.json) | Wilson 95% intervals: repair rate 3 of 8, 0.137 to 0.694; silent failure rate 2 of 3, 0.208 to 0.939; validation catch rate 8 of 8, 0.676 to 1.000. The v1.0 rates rest on very small counts and should be read with these intervals. |
| Supplementary set, 10 candidate records fed straight to the loop: numeric strings in typed fields and multi-defect records, labelled in supplement.json and committed before the runner existed (ROADMAP v1.1 items 1 and 2) | 10 of 10 records matched the label. Healed 6 (4 clean, 2 flagged), still rejected 4. Repair rate 0.600 (Wilson 95% 0.313 to 0.832), silent failure rate 0.333 (2 of 6: the two records where a coerced value was then clamped). The coercion rule applied 7 times; it applied 0 times in the v1.0 benchmark, because the Level 2 extractor already parses numeric tokens. A fractional string ("4.5") never became an integer, and a boolean was never coerced. |
| Differential check of the Level 1 subset validator against the jsonschema package (Draft 2020-12), tests/test_learn_differential.py | Agrees on all 9 parseable Level 1 case arguments and all 16 Level 2 candidate records. One deliberate, pinned disagreement: the subset rejects 60.0 for an integer field (Python types), the standard accepts it. |

Unit tests after the follow-up: 71 run, 71 passed (55 from v1.0, plus 6
uncertainty, 6 supplementary-set and 4 differential tests). The
research review is in docs/research-review.md.

## Fan-out

Written fan-out for v1.0 is in fanout/ (2026-11-04), graded in
PUBLICITY.md:

- fanout/blog-post.md: the full story, with the main results claim.
- fanout/tutorial.md: course module P14-structured-outputs-lab;
  every command in it was run and verified.
- fanout/website-page.md: project page copy only, not published.
- fanout/linkedin-post.md: draft, not posted, link in the first
  comment line only.
- fanout/paper-candidate.md: the self-healing parse reliability
  note brief; submission is Jesun's tap, nothing submitted.
- fanout/release-notes.md: draft notes for the existing releases
  v0.1, v0.5, and v1.0 only.

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

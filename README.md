# structured-outputs-lab

Reliable LLM applications: strict schemas, validated extraction, a self-healing parse loop.

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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

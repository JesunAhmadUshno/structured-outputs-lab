# structured-outputs-lab

Reliable LLM applications: strict schemas, validated extraction, a self-healing parse loop.

Status: LEARN DONE 2026-11-04 (ROADMAP-V3-BATCH, Sprint 1).
Level 1 code runs with 16 passing unit tests and one measured case
run (10 of 10 cases matched expectation, below). Build and Deep are
not started. The Wave 0 scaffold claim is superseded by this line.
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

## Novelty

PROPOSED. See NOVELTY.md. The novelty text is a draft until the Jev claim_check gate passes on it.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

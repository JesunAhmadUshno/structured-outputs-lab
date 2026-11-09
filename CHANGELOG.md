# Changelog

All notable changes to this project. Format: Keep a Changelog 1.1.
The tags v0.1, v0.5 and v1.0 were cut under the earlier Learn, Build,
Deep ladder; no release has been tagged under the portfolio standard
v2 yet.

## [Unreleased]

### Changed
- 2026-11-08: Adopted the portfolio standard v2. README is the abstract
  (question, headline with its interval, field, job family, verdict:
  Functional, not pre-registered). PROPOSAL.md holds SPEC.md,
  NOVELTY.md, DOSSIER.md, BUILD-SPEC.md and DEEP-SPEC.md, marked not
  locked: git history shows no hypotheses or pass lines committed
  before the results. REPORT.md holds the three level READMEs,
  ROADMAP.md (open backlog) and docs/research-review.md, and scores
  every written prediction with the field-profile misses. Self-assigned
  level, publicity, hiring-value and review grades left the public
  files (grades are internal). docs/index.md, the old Jekyll page, is
  removed: Pages is built by the Actions workflow from site/. The
  dashboard reads its limits and backlog from REPORT.md. CI gains
  `permissions: contents: read` and a layout test (required files, no
  public grade); CodeQL now covers the dashboard's JavaScript;
  Dependabot watches site/ npm. Decisions 0001 (layout) and 0002
  (repair rules) recorded.

## Earlier history (from git and the old README status lines)

### Security
- 2026-11-07: vite upgraded to 6.4.5 so npm audit reports no high or
  critical advisories.

### Added
- 2026-11-07: Follow-up: Wilson 95% intervals on every rate
  (uncertainty.py); a supplementary set of 10 records, labelled and
  committed before its runner, 10 of 10 matched; a differential test
  against jsonschema; CI fails if any committed results file differs
  after regeneration; the live dashboard with JS ports parity-checked
  against the Python results at build; Pages workflow. Unit tests after
  the follow-up: 71 run, 71 passed.
- 2026-11-05: Actions polish pack: CI on Python 3.11 and 3.12 with ruff,
  CodeQL, Dependabot, release, labeler, greetings, stale; docs/index.md
  page.
- 2026-11-04: Fan-out drafts in fanout/ (nothing posted or submitted).
- 2026-11-04 (tag v1.0): Level 3 Deep, compressed: self-healing parse
  loop over the 8 Build rejections, 8 of 8 matched the labelled
  outcome, repair rate 0.375, silent failure rate 0.667, 21 Deep tests
  (55 total). The rest of the Deep scope became the v1.1 backlog.
- 2026-11-04 (tag v0.5): Level 2 Build: extraction pipeline over 16
  synthetic documents, 16 of 16 matched, extraction accuracy 1.000,
  catch rate 1.000, 0 false accepts, 18 Build tests (34 total).
- 2026-11-04 (tag v0.1): Level 1 Learn: strict subset validator and
  function-calling dispatcher, 10 of 10 cases matched, 16 tests.
- 2026-11-04: Wave 0 scaffold: SPEC.md, DOSSIER.md v1, NOVELTY.md draft,
  level folders (Level 1 Learn, the core idea built small; Level 2
  Build, a working system; Level 3 Deep, evaluation and hard cases).
  Project P14, fleet node BlackBoxV3, Wave 2.

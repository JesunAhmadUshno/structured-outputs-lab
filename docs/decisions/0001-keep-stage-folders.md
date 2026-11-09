# 0001: Keep code and evidence in the three stage folders

Date: 2026-11-08. Status: accepted. Decided by: Jesun Ahmad Ushno.

## Context

The portfolio standard v2 lays a repo out as src/, experiments/ and
results/. This repo grew as level-1-learn/, level-2-build/ and
level-3-deep/, each holding its code, its labelled input set, its
runner and its scored results. The tests load modules from those
folders by path, CI regenerates the results files there and fails on
any byte difference, and the dashboard imports the same files at build
time. REPORT.md quotes a SHA-256 of level-3-deep/results_deep.json.

## Decision

Keep the three folders and their file names. The README layout table
maps each folder to its roles (code, evidence, results). The level
READMEs, the level specs and the root plan files move into
PROPOSAL.md and REPORT.md.

## Consequences

No path in the tests, CI, dashboard or recorded hashes changes, so the
results stay byte-identical across the migration. The folder names
still read as the old ladder; a later change can move them to src/,
experiments/ and results/ in one pull request if that matters more
than the churn.

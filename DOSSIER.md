# DOSSIER: structured-outputs-lab (P14) v1, 2026-11-04

Written under the documentation and publishing standard (past, present, future). Updated at ship time.

## Past

Prior art for this project is named in NOVELTY.md (schema libraries (Pydantic class) and JSON mode docs). The history of the problem, the key papers and systems, and what was tried before are recorded in the Roadmap v2 section text in SPEC.md and will be expanded with dated sources at the project's wave, before Build opens.

## Present

Current demand evidence: hiring value 3 of 5 (applied roles at 3 companies) [confirmed, fleet and scoring pass 2026-11-04; for P23 to P29, the decision pack 2026-11-04]. The Round 3 research (2026-11-04) found the market centre at post-training, evals, environments, and inference depth [confirmed as the research finding; the report is at ~/workspace/research_notes/roadmap-v3-revaluation-research-20261104-0949/report.md]. Tools and versions are pinned at Build time, not in this v1.

Built state, 2026-11-04: Level 1 Learn is done (strict schema validator and function-calling dispatcher, 16 tests, 10 of 10 cases matched). Level 2 Build is done the same day under the December Compression Protocol: a document extraction pipeline over a 16-document synthetic corpus in 3 types (invoice, meeting note, product listing), with deterministic regex extractors, one strict schema per type, every output validated with the Learn validator, and failures routed to a rejection list with validator error paths. Measured: extraction accuracy 1.000 (40 of 40 fields), validation catch rate 1.000 (8 of 8 malformed documents), 0 false accepts, 18 Build tests (34 total). Level 3 Deep is done the same day as compressed Deep, and the project is at v1.0 ship state: a self-healing parse loop over the 8 Build rejections, with deterministic named repair rules (drop additional field, coerce a cleanly parsing numeric string, flagged clamp to range), every repair attempt logged, missing fields never invented and invalid enum values never guessed, the loop bounded at 3 rounds. Measured on an expected healed outcome set labelled before the run: 8 of 8 documents matched the labelled outcome, 3 healed and 5 still rejected, repair rate 0.375 (1 clean heal, 2 flagged clamps), silent failure rate 0.667 (both clamped heals state values the documents did not), 0 of 8 Build-accepted records altered, 21 Deep tests (55 total). Full record: level-3-deep/README.md and level-3-deep/results_deep.json. The rest of the v2 Deep scope is the v1.1 backlog in ROADMAP.md.

## Future

Open problems and the project's next steps sit in the Deep level scope in SPEC.md. Any forecast about this field is [unverified] unless a dated primary source is added here at the wave update.

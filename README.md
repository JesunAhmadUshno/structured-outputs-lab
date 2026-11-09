# structured-outputs-lab

**Question.** Can a bounded, rule-based repair loop raise the share of
schema-valid records without introducing false values, and how often
does a "healed" record state something the source did not?

**Headline.** On the 8 designed malformed records, the repair loop healed 3 (repair rate 0.375, Wilson 95% 0.137 to 0.694), and 2 of those 3 were flagged clamps that changed a stated value (silent failure rate 0.667, 95% 0.208 to 0.939); no language-model output was measured.

**Field.** ML and AI research. **Job family.** Applied AI engineering
(reliable LLM applications: strict schemas, validated extraction).

**Verdict.** Functional, not pre-registered. Tests pass in CI on Python
3.11 and 3.12, the system under study (validator, extraction pipeline,
repair loop) runs end to end in one command, and CI fails unless every
committed results file regenerates byte for byte. No plan was locked
before the results existed, so the repo is capped at Functional until a
confirmatory cycle runs under a tagged proposal. The old tags v0.1,
v0.5 and v1.0 come from the earlier Learn, Build, Deep ladder and do
not mean "v1.0 Released" under the current standard.

Live dashboard: https://jesunahmadushno.github.io/structured-outputs-lab/
(source in site/; in-browser ports of the validator, pipeline and repair
loop, checked against the committed results on every build.)

## Reproduce

```text
python level-1-learn/run_cases.py
python level-2-build/run_build.py
python level-3-deep/run_deep.py
python level-3-deep/run_supplement.py
python level-3-deep/uncertainty.py
git diff --exit-code -- level-2-build/results_build.json level-3-deep/results_deep.json level-3-deep/results_supplement.json level-3-deep/uncertainty.json
python -m unittest discover -s tests -p "test_*.py" -v
```

Python standard library only. The differential test also uses the
reference validator (`pip install jsonschema==4.26.0`) and is skipped
where it is absent. CPU only, a few seconds in total.

## Lifecycle

- Question: DONE 2026-11-04
- Proposal: NOT PRE-REGISTERED 2026-11-08
- Baseline: DONE 2026-11-04
- Build: DONE 2026-11-04
- Evaluate: OPEN
- Report: DRAFT 2026-11-08
- Review: OPEN
- Release: OPEN

Evaluate stays open because the ML and AI research profile is not met:
no model baseline and no registered ablation (REPORT.md, Hypotheses
scored).

## Layout

The code and its evidence stay in the three stage folders, because the
tests, the CI reproduce check and the dashboard read them there
(docs/decisions/0001).

| Path | Role | What it holds |
| --- | --- | --- |
| PROPOSAL.md | proposal | The plan as it was written, not locked: scope, prior work, proposed novelty, the pipeline and repair-loop designs |
| REPORT.md | report | Current state, hypotheses scored with misses, results, limits, failure modes, the 2026-11-07 review, open backlog |
| level-1-learn/ | code, evidence | Subset JSON Schema validator, function-calling dispatcher, the 10 labelled cases and their runner |
| level-2-build/ | code, evidence, results | Synthetic corpus, extractors and schemas, labelled evaluation set, runner, results_build.json |
| level-3-deep/ | code, evidence, results | Repair loop, labelled sets (evaluation_deep.json, supplement.json), runners, results_deep.json, results_supplement.json, uncertainty.json |
| tests/ | tests | Unit tests per stage, the jsonschema differential test, and the layout test |
| docs/decisions/ | decisions | Records of hard-to-reverse choices |
| site/ | dashboard | The live dashboard, built from the files above |
| fanout/, PUBLICITY.md | outreach | Dated 2026-11-04 drafts (nothing posted) and the channel log |
| CHANGELOG.md, CITATION.cff, SECURITY.md, LICENSE | release | History, citation, how to report a vulnerability, licence |

There is no separate experiments/ or results/ folder: each labelled
input set and its scored results sit beside the runner that produces
them. Older files and commit messages name files that moved here on
2026-11-08: SPEC.md, NOVELTY.md, DOSSIER.md, BUILD-SPEC.md and
DEEP-SPEC.md are now in PROPOSAL.md; the level READMEs, ROADMAP.md and
docs/research-review.md are now in REPORT.md.

## License

Code: Apache-2.0 (see LICENSE). Tutorials: CC BY 4.0. Ruled in D-V3-11, 2026-11-04.

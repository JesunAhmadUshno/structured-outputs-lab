# Website project page copy: structured-outputs-lab

Site: jesunahmadushno.com
Status: COPY ONLY, draft for the project page. Dated 2026-11-04.
Nothing on any website was changed by this file.

## Headline

structured-outputs-lab: strict schemas, validated extraction, and a self-healing parse loop that never invents data

## Summary

structured-outputs-lab is an open project on reliable LLM
applications built by Jesun Ahmad Ushno as project P14 in
Roadmap v3. It builds the defence against malformed structured
output in three levels: a strict schema validator with a
validate-then-dispatch gate for function calling, a document
extraction pipeline that validates every output against one
strict schema per document type, and a self-healing parse loop
that repairs only under named deterministic rules, logs every
attempt, and never invents a missing field or guesses an enum
value. It runs on the Python 3.12 standard library only, with no
language model, no API, and no credential.

Status: v1.0, 2026-11-04. Learn, Build, and compressed Deep are
done. Total tests: 55, all passing at v1.0.

## Results

All results below are measured runs on synthetic designed sets,
recorded in the level READMEs in the GitHub repo. They prove the
gate, the pipeline mechanism, and the loop discipline, not
production quality on real documents or real model output.

| Level | Set | Headline result | Notes |
| --- | --- | --- | --- |
| Learn | 10 model-style cases against strict schemas | 10 of 10 matched; 4 dispatched, 6 rejected at named error paths | Error paths $.unit, $.date twice, $.room, $.keywords[1], $; 16 tests |
| Build | 16 synthetic documents in 3 types | 16 of 16 matched; 8 accepted, 8 rejected; extraction 40 of 40 fields; catch rate 8 of 8; 0 false accepts | Deterministic regex extractors; Learn validator reused unchanged; 18 tests, 34 total |
| Deep (compressed) | The 8 Build rejections, labelled outcomes | 8 of 8 matched; 3 healed, 5 still rejected; repair rate 0.375; silent failure rate 0.667; 0 of 8 accepted records altered | Only clean heal is the additional field drop; both other heals are flagged clamps; repair rules named only, no invented data; 21 tests, 55 total |

## Honest limits

- Synthetic designed sets only, at every level, one defect per
  malformed document at Build and Deep.
- No language model is involved in v1.0. The extractors are
  deterministic and regex based over one fixed line format per
  type.
- The validator is a strict subset of JSON Schema.
- Validation proves shape, not truth.
- Compressed Deep is not the full v2 Deep scope. The remainder is
  the v1.1 backlog in the repo ROADMAP.md.

## Links

- GitHub repo: https://github.com/JesunAhmadUshno/structured-outputs-lab
- Release v0.1 (Learn): https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.1
- Release v0.5 (Build): https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.5
- Release v1.0 (Learn, Build, compressed Deep): https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v1.0
- Tutorial: fanout/tutorial.md in the GitHub repo
- Blog post draft: fanout/blog-post.md in the GitHub repo

## License note

Code: Apache-2.0. Tutorials: CC BY 4.0.

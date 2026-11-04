# Level 2, Build: structured-outputs-lab

Status: DONE 2026-11-04 (ROADMAP-V3-BATCH, Sprint 1 of the December
Compression Protocol). Evidence: the code in this folder, 18 Build
unit tests in tests/test_build_pipeline.py (34 tests total with
Learn), and the measured pipeline run recorded below and in
results_build.json, written by the runner. Deep is not started.
Spec for this level: BUILD-SPEC.md in this folder.

## What was built

A document extraction pipeline with schema validation on every
output, Python standard library only:

1. Corpus (corpus.py): 16 synthetic documents in 3 types (invoice,
   meeting note, product listing), authored for this level and
   labelled synthetic. Eight documents are well formed. Eight are
   deliberately malformed, each with exactly one designed defect:
   missing field (2), wrong type (2), extra field (1),
   out-of-range value (2), invalid enum value (1).
2. Extractors (pipeline.py): one deterministic extractor per type,
   regex and rule based. No language model is involved, and
   nothing here claims one is. Typed fields are converted only
   when the token parses cleanly (Total: 249.50 becomes the number
   249.5). A token that does not parse stays a string, so the
   validator reports the type error instead of the extractor
   hiding it.
3. Schemas (pipeline.py): one strict schema per type. Invoice:
   invoice_id (pattern INV plus 4 digits), vendor, date, total_cad
   (number, 0.01 to 100000), items_count (integer, 1 to 100).
   Meeting note: meeting_id (pattern MTG plus 4 digits), title,
   date, attendees (array of strings, 1 to 20), duration_minutes
   (integer, 15 to 480). Product listing: sku (pattern SKU plus 4
   digits), name, price_cad (number, 0.01 to 50000), stock
   (integer, 0 to 10000), category (enum: tools, kitchen, office,
   outdoor). Every schema requires all five fields and sets
   additionalProperties False.
4. Validation: every extracted record is validated with the Level
   1 Learn validator (level-1-learn/schema_validate.py), reused
   unchanged. The pipeline reuses the Learn lesson directly: shape
   is checked by the same code that guarded function calling.
5. Routing: a record with no validation errors goes to the
   accepted list. A record with any error goes to the rejection
   list with the full validator errors, paths included. An invalid
   extraction is never silently passed, coerced, or repaired at
   this level. Unknown document types are rejected with a
   structured unknown_type error at path $.

## Run it

```text
python level-2-build/run_build.py
python -m unittest discover -s tests -p "test_build*.py" -v
```

No dependencies. Python 3.12 standard library only.

## Measured results (2026-11-04, Muse VM, Python 3.12.3)

Method: the evaluation set (evaluation.json) was labelled before
the run. For each document it states the expected outcome: accept
with the expected record fields, or reject with the named first
error path and the designed defect. The runner compares the
pipeline outcome with that expectation for all 16 documents.
Extraction accuracy counts fields on the 8 expected-accept
documents only (fields correct divided by fields total, 5 fields
per document). Validation catch rate counts the 8 malformed
documents (correctly rejected divided by malformed total). False
accepts are malformed documents the pipeline accepted. The full
per-document record, including each extracted record and each
error list, is in results_build.json, written by the runner. The
runner was run twice and wrote identical results_build.json both
times.

| Document | Type | Expected | Actual | First error path | Fields | Match |
| --- | --- | --- | --- | --- | --- | --- |
| d01-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d02-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d03-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d04-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d05-product-valid | product_listing | accept | accept | - | 5/5 | MATCH |
| d06-product-valid | product_listing | accept | accept | - | 5/5 | MATCH |
| d07-invoice-valid | invoice | accept | accept | - | 5/5 | MATCH |
| d08-meeting-valid | meeting_note | accept | accept | - | 5/5 | MATCH |
| d09-invoice-missing-vendor | invoice | reject | reject | $.vendor | - | MATCH |
| d10-invoice-bad-total-type | invoice | reject | reject | $.total_cad | - | MATCH |
| d11-invoice-extra-field | invoice | reject | reject | $.discount | - | MATCH |
| d12-invoice-total-out-of-range | invoice | reject | reject | $.total_cad | - | MATCH |
| d13-meeting-missing-title | meeting_note | reject | reject | $.title | - | MATCH |
| d14-meeting-duration-out-of-range | meeting_note | reject | reject | $.duration_minutes | - | MATCH |
| d15-product-bad-stock-type | product_listing | reject | reject | $.stock | - | MATCH |
| d16-product-bad-category | product_listing | reject | reject | $.category | - | MATCH |

Summary numbers: 16 of 16 documents matched expectation, 8
accepted and 8 rejected. Extraction accuracy on accepted docs:
40 of 40 fields correct (1.000). Validation catch rate on
malformed docs: 8 of 8 caught (1.000). False accepts: 0, with
evidence in the table above: every malformed row shows actual
reject at its designed first error path, and the pipeline split
test asserts the same 8 and 8 split. Unit tests: 18 Build tests
pass, 34 tests total with Learn (16 Learn plus 18 Build), plus
the scaffold smoke test.

Read the numbers honestly: 1.000 on both rates over 16 short
synthetic documents proves the pipeline mechanism end to end: the
extractors read the format they were written for, and the
validator stops every designed defect at its field. It does not
prove extraction on real documents, which vary in layout, carry
noise, and break line formats this corpus never shows.

Summary claim: Level 2 Build of structured-outputs-lab, 2026-11-04: a dependency-free document extraction pipeline (deterministic regex and rule based extractors, one strict schema per type, every output validated with the Level 1 validator, failures routed to a rejection list with validator error paths) over a 16-document synthetic corpus in 3 types (invoice, meeting note, product listing) scored, on an evaluation set labelled before the run, extraction accuracy 1.000 (40 of 40 fields correct on the 8 expected-accept documents), validation catch rate 1.000 (8 of 8 malformed documents rejected, each at its designed first error path), and 0 false accepts. 18 Build unit tests pass, 34 tests total with Learn.

## Limits, stated plainly

- The extractors are regex and rule based over one fixed line
  format per type. A document that renames a label, wraps a value
  across lines, or changes order conventions can extract wrongly
  or incompletely. No language model and no layout analysis exist
  at this level.
- The corpus is 16 synthetic documents written against the same
  format the extractors read. No claim about real-world accuracy,
  scale, or latency is made or implied.
- Each malformed document carries exactly one defect. Real bad
  extractions carry several at once; the validator reports all of
  them, but this set measures only the first error path.
- Validation proves shape, not truth. An invoice whose total is
  in range but wrong for its items passes. Semantic cross-checks
  belong to the caller.
- Rejected records are listed, not repaired. The self-healing
  parse loop that repairs from structured errors is Deep scope.
- The run executed on the Muse VM (CPU), not the assigned
  BlackBoxV3 fleet node. Nothing at this size needs the fleet node.

## Next

Level 3, Deep: a self-healing parse loop with every repair logged
per SPEC.md, including the repair rate and the silent failure
rate, with the failure modes written.

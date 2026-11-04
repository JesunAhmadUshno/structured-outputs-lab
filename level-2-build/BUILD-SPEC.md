# Build Spec: structured-outputs-lab Level 2

## Objective
Close Build per SPEC.md acceptance: the system runs end to end,
tests pass, and one benchmark table with method is in the README.
Build is a document extraction pipeline with schema validation on
every output:

1. A small synthetic document corpus (16 documents, 3 document
   types: invoice, meeting note, product listing), labelled
   synthetic in the corpus file and in every report. Documents are
   plain line-based text, the shape a scanned or emailed document
   takes after a plain text pass.
2. One deterministic extractor per type (regex and rule based,
   Python standard library only). Extractors are labelled honestly:
   no language model is involved at this level, and no file claims
   one is. Each extractor returns a candidate record.
3. One strict schema per type, validated with the Level 1 Learn
   validator (level-1-learn/schema_validate.py), reused unchanged.
   Strict means required fields, typed fields, ranges, patterns,
   enums where the type has them, and additionalProperties False.
4. A pipeline that extracts, validates every output, and routes
   each document to exactly one of two lists: accepted (record
   passed validation) or rejected (record plus the validator
   errors, with paths). An invalid extraction is never silently
   passed, coerced, or repaired at this level. Repair is Deep
   scope.
5. Deliberately malformed documents in the corpus (8 of 16) that
   must be rejected: missing field, wrong type, extra field,
   out-of-range value, and invalid enum value, so the rejection
   path is measured, not just claimed.

## Assumptions
- Python standard library only. No external model, API, credential,
  or spend. No network.
- The corpus and the evaluation set are synthetic and labelled as
  synthetic. They prove the extraction and validation mechanism end
  to end, not production extraction quality on real documents.
- The evaluation set (evaluation.json) states the expected outcome
  per document before the run: accept with expected key fields, or
  reject with the named first error path.

## Commands
- Test: python -m unittest discover -s tests -p "test_build*.py" -v
- Run: python level-2-build/run_build.py
- Full: python -m unittest discover -s tests -v

## Boundaries
- Always: stdlib only, deterministic extractors, the Learn
  validator reused unchanged, results recorded exactly as
  measured, malformed documents labelled as designed defects.
- Never: an external call, a new credential, a language model
  claim, a silent pass of an invalid record, a coercion that hides
  a type error (a non-numeric total stays a string so the validator
  rejects it), or a grade for a scaffold.

## Success criteria
- Each extractor returns the exact expected record for the valid
  documents of its type.
- Every malformed document is rejected at its designed first
  error path. False accepts are reported even if zero.
- Extraction accuracy on expected-accept documents (fields correct
  divided by fields total), validation catch rate on malformed
  documents, and the false accept count are printed by the runner
  and stored in results_build.json.
- The runner is deterministic: two runs write identical
  results_build.json.
- At least 12 Build tests pass; Learn tests still pass.

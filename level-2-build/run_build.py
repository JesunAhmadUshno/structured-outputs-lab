"""Run the Level 2 Build extraction pipeline over the corpus.

Usage: python level-2-build/run_build.py

Method: the evaluation set (evaluation.json) was labelled before
the run. For each of the 16 synthetic documents it states the
expected outcome: accept with the expected record fields, or reject
with the named first error path and the designed defect. The runner
feeds every document through the pipeline and compares:

- outcome (accept or reject) against the expectation,
- for expected-accept documents, each extracted field against the
  expected fields (extraction accuracy is fields correct divided
  by fields total over those documents),
- for expected-reject documents, the first validator error path
  against the named path (validation catch rate is malformed
  documents correctly rejected divided by malformed documents),
- false accepts: malformed documents the pipeline accepted. The
  count is reported even when it is zero.

The full per-document record is written to results_build.json
beside this file. The output is deterministic: no timestamps, keys
sorted, so two runs write identical files. Exit code 0 when every
document matches its expectation, 1 otherwise.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from corpus import DOCUMENTS  # noqa: E402
from pipeline import extract_and_validate  # noqa: E402


def load_evaluation():
    with open(os.path.join(HERE, "evaluation.json"), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    evaluation = {entry["id"]: entry for entry in load_evaluation()}
    per_document = []
    fields_correct = 0
    fields_total = 0
    malformed_total = 0
    malformed_caught = 0
    false_accepts = 0
    matched = 0
    print(
        "id                               type             expected  actual    "
        "first error path  fields  match"
    )
    for document in DOCUMENTS:
        expected = evaluation[document["id"]]
        outcome = extract_and_validate(document)
        actual = "accept" if outcome["accepted"] else "reject"
        want = "accept" if expected["expect_ok"] else "reject"
        first_path = "-"
        if outcome["errors"]:
            first_path = outcome["errors"][0]["path"]
        doc_fields_correct = None
        doc_fields_total = None
        ok = actual == want
        if expected["expect_ok"]:
            doc_fields_total = len(expected["expected_fields"])
            doc_fields_correct = sum(
                1
                for field, value in expected["expected_fields"].items()
                if outcome["record"] is not None
                and outcome["record"].get(field) == value
            )
            fields_total += doc_fields_total
            fields_correct += doc_fields_correct
            if doc_fields_correct != doc_fields_total:
                ok = False
        else:
            malformed_total += 1
            if not outcome["accepted"]:
                malformed_caught += 1
                if first_path != expected["expect_first_path"]:
                    ok = False
            else:
                false_accepts += 1
        matched += 1 if ok else 0
        fields_view = "-"
        if doc_fields_total is not None:
            fields_view = f"{doc_fields_correct}/{doc_fields_total}"
        print(
            f"{document['id']:<32} {document['doc_type']:<16} "
            f"{want:<9} {actual:<9} {first_path:<17} "
            f"{fields_view:<7} {'MATCH' if ok else 'MISMATCH'}"
        )
        per_document.append(
            {
                "id": document["id"],
                "doc_type": document["doc_type"],
                "expected": want,
                "actual": actual,
                "first_error_path": None if first_path == "-" else first_path,
                "expected_first_error_path": expected.get("expect_first_path"),
                "defect": expected.get("defect"),
                "fields_correct": doc_fields_correct,
                "fields_total": doc_fields_total,
                "record": outcome["record"],
                "errors": outcome["errors"],
                "match": ok,
            }
        )
    accuracy = fields_correct / fields_total if fields_total else 0.0
    catch_rate = malformed_caught / malformed_total if malformed_total else 0.0
    accepted_count = sum(1 for row in per_document if row["actual"] == "accept")
    print(
        f"summary: {matched} of {len(DOCUMENTS)} documents matched expectation; "
        f"{accepted_count} accepted, {len(DOCUMENTS) - accepted_count} rejected"
    )
    print(
        f"extraction accuracy on accepted docs: {fields_correct} of "
        f"{fields_total} fields correct ({accuracy:.3f})"
    )
    print(
        f"validation catch rate on malformed docs: {malformed_caught} of "
        f"{malformed_total} caught ({catch_rate:.3f})"
    )
    print(f"false accepts: {false_accepts}")
    results = {
        "documents": len(DOCUMENTS),
        "types": sorted({d["doc_type"] for d in DOCUMENTS}),
        "summary": {
            "matched": matched,
            "accepted": accepted_count,
            "rejected": len(DOCUMENTS) - accepted_count,
            "fields_correct": fields_correct,
            "fields_total": fields_total,
            "extraction_accuracy": round(accuracy, 3),
            "malformed_total": malformed_total,
            "malformed_caught": malformed_caught,
            "validation_catch_rate": round(catch_rate, 3),
            "false_accepts": false_accepts,
        },
        "per_document": per_document,
    }
    out_path = os.path.join(HERE, "results_build.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    print(f"results written: {out_path}")
    return 0 if matched == len(DOCUMENTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())

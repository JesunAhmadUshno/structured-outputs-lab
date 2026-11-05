"""Run the Level 3 Deep self-healing loop over the Build rejections.

Usage: python level-3-deep/run_deep.py

Method: the expected healed outcome set (evaluation_deep.json)
was labelled before the run. For each of the 8 documents the
Level 2 pipeline rejects it states the defect class, whether a
heal is expected, whether a flagged value-changing heal is
expected, the true record, and, where a truthful healed record
exists, that record exactly. The runner:

- runs the Level 2 pipeline over the corpus and takes its
  rejected list as the loop input (attempted),
- feeds each rejected record to heal.attempt_heal through
  heal.heal_rejected,
- counts healed (split clean and flagged), still rejected,
  repair rate (healed divided by attempted),
- counts silent failures under the DEEP-SPEC definition: a
  healed record is correct only when a truthful healed record
  exists in the labelled set and the healed record equals it,
  so a flagged clamp heal, which has no truthful healed record,
  counts as a silent failure. Silent failure rate is silent
  failures divided by healed,
- breaks the same counts down per defect class,
- feeds every Build-accepted record to the loop and counts how
  many are altered (must be 0).

The full per-document record, including each repair log, is
written to results_deep.json beside this file. The output is
deterministic: no timestamps, keys sorted, so two runs write
identical files. Exit code 0 when every document ends in its
labelled outcome and no accepted record is altered, 1 otherwise.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

from corpus import DOCUMENTS  # noqa: E402
from heal import heal_rejected  # noqa: E402
from pipeline import run_pipeline  # noqa: E402

DEFECT_CLASSES = ["missing", "wrong_type", "extra_field", "out_of_range", "bad_enum"]


def load_evaluation():
    with open(os.path.join(HERE, "evaluation_deep.json"), encoding="utf-8") as fh:
        return json.load(fh)


def evaluate():
    """Run the whole Deep evaluation. Returns the results dict."""
    evaluation = {entry["id"]: entry for entry in load_evaluation()}
    accepted, rejected = run_pipeline(DOCUMENTS)

    valid_altered = 0
    for outcome in accepted:
        healed = heal_rejected(outcome)
        if healed["status"] != "already_valid" or healed["record"] != outcome["record"]:
            valid_altered += 1

    per_document = []
    healed_total = 0
    healed_clean = 0
    healed_flagged = 0
    silent_failures = 0
    matched = 0
    per_class = {
        cls: {"attempted": 0, "healed": 0, "healed_flagged": 0, "silent_failures": 0}
        for cls in DEFECT_CLASSES
    }
    for outcome in rejected:
        expected = evaluation[outcome["id"]]
        cls = expected["defect_class"]
        result = heal_rejected(outcome)
        is_healed = result["healed"]
        silent = False
        if is_healed:
            healed_total += 1
            if result["flagged"]:
                healed_flagged += 1
            else:
                healed_clean += 1
            truthful = expected["truthful_healed_record"]
            correct = truthful is not None and result["record"] == truthful
            silent = not correct
            if silent:
                silent_failures += 1
        per_class[cls]["attempted"] += 1
        if is_healed:
            per_class[cls]["healed"] += 1
            if result["flagged"]:
                per_class[cls]["healed_flagged"] += 1
            if silent:
                per_class[cls]["silent_failures"] += 1
        ok = is_healed == expected["expect_healed"]
        if is_healed and result["flagged"] != expected["expect_flagged"]:
            ok = False
        if is_healed and expected["truthful_healed_record"] is not None:
            if result["record"] != expected["truthful_healed_record"]:
                ok = False
        if result["record"] == outcome["record"] and is_healed:
            ok = False
        matched += 1 if ok else 0
        per_document.append(
            {
                "id": outcome["id"],
                "doc_type": outcome["doc_type"],
                "defect_class": cls,
                "expected_healed": expected["expect_healed"],
                "expected_flagged": expected["expect_flagged"],
                "healed": is_healed,
                "status": result["status"],
                "flagged": result["flagged"],
                "silent_failure": silent if is_healed else None,
                "rounds": result["rounds"],
                "original_record": outcome["record"],
                "final_record": result["record"],
                "repair_log": result["repair_log"],
                "final_errors": result["errors"],
                "match": ok,
            }
        )

    attempted = len(rejected)
    repair_rate = healed_total / attempted if attempted else 0.0
    silent_rate = silent_failures / healed_total if healed_total else 0.0
    return {
        "attempted_from_build_rejections": attempted,
        "build_accepted_checked": len(accepted),
        "summary": {
            "attempted": attempted,
            "healed": healed_total,
            "healed_clean": healed_clean,
            "healed_flagged": healed_flagged,
            "still_rejected": attempted - healed_total,
            "repair_rate": round(repair_rate, 3),
            "silent_failures": silent_failures,
            "silent_failure_rate": round(silent_rate, 3),
            "valid_records_altered": valid_altered,
            "matched": matched,
        },
        "per_defect_class": per_class,
        "per_document": per_document,
    }


def main():
    results = evaluate()
    summary = results["summary"]
    print(
        "id                               class         expected  actual          "
        "flagged  silent  rounds  match"
    )
    for row in results["per_document"]:
        expected = "heal" if row["expected_healed"] else "reject"
        actual = row["status"]
        silent_view = "-"
        if row["silent_failure"] is not None:
            silent_view = "yes" if row["silent_failure"] else "no"
        print(
            f"{row['id']:<32} {row['defect_class']:<13} {expected:<9} "
            f"{actual:<15} {str(row['flagged']):<8} {silent_view:<7} "
            f"{row['rounds']:<7} {'MATCH' if row['match'] else 'MISMATCH'}"
        )
    print(
        f"summary: {summary['matched']} of {summary['attempted']} rejected "
        f"documents matched the labelled outcome; {summary['healed']} healed "
        f"({summary['healed_clean']} clean, {summary['healed_flagged']} "
        f"flagged), {summary['still_rejected']} still rejected"
    )
    print(
        f"repair rate: {summary['healed']} of {summary['attempted']} "
        f"({summary['repair_rate']:.3f})"
    )
    print(
        f"silent failure rate: {summary['silent_failures']} of "
        f"{summary['healed']} healed ({summary['silent_failure_rate']:.3f})"
    )
    print(f"valid records altered: {summary['valid_records_altered']}")
    out_path = os.path.join(HERE, "results_deep.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    print(f"results written: {out_path}")
    ok = (
        summary["matched"] == summary["attempted"]
        and summary["valid_records_altered"] == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

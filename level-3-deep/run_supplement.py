"""Run the self-healing loop over the supplementary labelled set.

Usage: python level-3-deep/run_supplement.py

Why a supplement: the v1.0 benchmark (run_deep.py) never exercises
the coerce_numeric_string rule and holds one defect per document.
The regex extractor converts numeric tokens itself, so a numeric
string can never reach the loop through the Level 2 pipeline. This
set therefore feeds candidate records directly, in the shape a
model's JSON output would take: numeric strings in typed fields,
and records with two or three defects at once (ROADMAP v1.1 items
1 and 2). It does not change or replace the v1.0 numbers.

Method: supplement.json was labelled and committed before this
runner existed. Per record it states the expected status, the
expected number of rounds, and the truthful healed record where one
exists. Repair rate and silent failure rate use the same
definitions as run_deep.py. Output is deterministic (keys sorted,
no timestamps). Exit code 0 when every record matches its label.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

from heal import attempt_heal  # noqa: E402
from pipeline import SCHEMAS  # noqa: E402


def evaluate():
    with open(os.path.join(HERE, "supplement.json"), encoding="utf-8") as fh:
        labelled = json.load(fh)
    per_record = []
    healed = clean = flagged = silent = matched = rule_uses = 0
    coerce_applied = 0
    for entry in labelled:
        result = attempt_heal(entry["record"], SCHEMAS[entry["doc_type"]], doc_id=entry["id"])
        truthful = entry["truthful_healed_record"]
        is_silent = None
        if result["healed"]:
            healed += 1
            flagged += 1 if result["flagged"] else 0
            clean += 0 if result["flagged"] else 1
            is_silent = not (truthful is not None and result["record"] == truthful)
            silent += 1 if is_silent else 0
        coerce_applied += sum(
            1 for e in result["repair_log"] if e["rule"] == "coerce_numeric_string" and e["outcome"] == "applied"
        )
        rule_uses += sum(1 for e in result["repair_log"] if e["outcome"].startswith("applied"))
        ok = result["status"] == entry["expect_status"] and result["rounds"] == entry["expect_rounds"]
        if truthful is not None and result["record"] != truthful:
            ok = False
        matched += 1 if ok else 0
        per_record.append(
            {
                "id": entry["id"],
                "doc_type": entry["doc_type"],
                "defects": entry["defects"],
                "expected_status": entry["expect_status"],
                "status": result["status"],
                "rounds": result["rounds"],
                "silent_failure": is_silent,
                "final_record": result["record"],
                "repair_log": result["repair_log"],
                "final_errors": result["errors"],
                "match": ok,
            }
        )
    attempted = len(labelled)
    return {
        "summary": {
            "attempted": attempted,
            "healed": healed,
            "healed_clean": clean,
            "healed_flagged": flagged,
            "still_rejected": attempted - healed,
            "repair_rate": round(healed / attempted, 3),
            "silent_failures": silent,
            "silent_failure_rate": round(silent / healed, 3) if healed else 0.0,
            "coerce_repairs_applied": coerce_applied,
            "repairs_applied": rule_uses,
            "matched": matched,
        },
        "per_record": per_record,
    }


def main():
    results = evaluate()
    print("id                                                      expected        actual          rounds  match")
    for row in results["per_record"]:
        print(f"{row['id']:<55} {row['expected_status']:<15} {row['status']:<15} {row['rounds']:<7} "
              f"{'MATCH' if row['match'] else 'MISMATCH'}")
    s = results["summary"]
    print(f"summary: {s['matched']} of {s['attempted']} matched the label; healed {s['healed']} "
          f"({s['healed_clean']} clean, {s['healed_flagged']} flagged), repair rate {s['repair_rate']:.3f}, "
          f"silent failure rate {s['silent_failure_rate']:.3f}, coercions applied {s['coerce_repairs_applied']}")
    out_path = os.path.join(HERE, "results_supplement.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    print(f"results written: {out_path}")
    return 0 if s["matched"] == s["attempted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

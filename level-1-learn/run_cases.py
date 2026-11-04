"""Run the Level 1 function-calling cases and print the outcome table.

Usage: python level-1-learn/run_cases.py
Exit code 0 when every case matches its expected outcome, 1 otherwise.
Each case states what SHOULD happen (expect_ok). A case where the
dispatcher accepts arguments the case says must be rejected is a real
failure of the guard, so the runner reports it and exits nonzero.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from function_calling import build_default_registry  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as fh:
        cases = json.load(fh)
    registry = build_default_registry()
    matched = 0
    print("case                              expected  actual    first error path  match")
    for case in cases:
        outcome = registry.call(case["function"], case["arguments"])
        expected = "accept" if case["expect_ok"] else "reject"
        actual = "accept" if outcome["ok"] else "reject"
        first_path = "-"
        if not outcome["ok"] and outcome["errors"]:
            first_path = outcome["errors"][0]["path"]
        ok = actual == expected
        if ok and not case["expect_ok"] and "expect_first_path" in case:
            ok = first_path == case["expect_first_path"]
        matched += 1 if ok else 0
        print(
            f"{case['id']:<33} {expected:<9} {actual:<9} "
            f"{first_path:<17} {'MATCH' if ok else 'MISMATCH'}"
        )
    dispatched = sum(registry.call_counts.values())
    print(
        f"summary: {matched} of {len(cases)} cases matched expectation; "
        f"{dispatched} calls dispatched to functions, "
        f"{len(cases) - dispatched} rejected before dispatch"
    )
    print("call counts:", registry.call_counts)
    return 0 if matched == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())

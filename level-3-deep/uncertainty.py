"""Uncertainty on the measured rates: Wilson 95% score intervals.

Usage: python level-3-deep/uncertainty.py

The Level 2 and Level 3 rates rest on very small counts (8
malformed documents, 3 healed records). A point estimate such as
a repair rate of 0.375 hides how little 8 trials can pin down, so
this script reads the committed results files and writes
uncertainty.json with a Wilson score interval for each rate. It
reads only results_build.json, results_deep.json and
results_supplement.json, runs no
pipeline, and is deterministic (keys sorted, values rounded to 4
digits), so two runs write identical files.

The Wilson interval is used instead of the plain normal interval
because it stays inside 0 to 1 and behaves sensibly at 0 of n and
n of n, which is exactly where these counts sit.
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
Z95 = 1.959963984540054  # two-sided 95% standard normal quantile


def wilson(successes, trials, z=Z95):
    """Wilson score interval for successes out of trials. Returns (lo, hi)."""
    if trials <= 0:
        raise ValueError("trials must be positive")
    p = successes / trials
    z2 = z * z
    denom = 1 + z2 / trials
    centre = (p + z2 / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def _entry(successes, trials, source):
    lo, hi = wilson(successes, trials)
    return {
        "successes": successes,
        "trials": trials,
        "point": round(successes / trials, 4),
        "wilson95": [round(lo, 4), round(hi, 4)],
        "source": source,
    }


def build_report():
    with open(os.path.join(ROOT, "level-2-build", "results_build.json"), encoding="utf-8") as fh:
        build = json.load(fh)["summary"]
    with open(os.path.join(HERE, "results_deep.json"), encoding="utf-8") as fh:
        deep = json.load(fh)["summary"]
    with open(os.path.join(HERE, "results_supplement.json"), encoding="utf-8") as fh:
        supp = json.load(fh)["summary"]
    return {
        "method": "Wilson score interval, 95%, z = 1.959964",
        "extraction_accuracy": _entry(
            build["fields_correct"], build["fields_total"], "level-2-build/results_build.json"
        ),
        "validation_catch_rate": _entry(
            build["malformed_caught"], build["malformed_total"], "level-2-build/results_build.json"
        ),
        "repair_rate": _entry(deep["healed"], deep["attempted"], "level-3-deep/results_deep.json"),
        "silent_failure_rate": _entry(deep["silent_failures"], deep["healed"], "level-3-deep/results_deep.json"),
        "supplement_repair_rate": _entry(supp["healed"], supp["attempted"], "level-3-deep/results_supplement.json"),
        "supplement_silent_failure_rate": _entry(
            supp["silent_failures"], supp["healed"], "level-3-deep/results_supplement.json"
        ),
    }


def main():
    report = build_report()
    for name in sorted(k for k in report if k != "method"):
        e = report[name]
        print(f"{name}: {e['successes']} of {e['trials']} = {e['point']:.3f}, "
              f"95% Wilson {e['wilson95'][0]:.3f} to {e['wilson95'][1]:.3f}")
    out_path = os.path.join(HERE, "uncertainty.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"results written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

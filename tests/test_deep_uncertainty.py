"""Uncertainty on the Level 3 rates (Wilson 95% score intervals).

The expected bounds below were worked out by hand from the Wilson
formula before the module existed: 3 of 8 healed gives about
0.137 to 0.694, 2 of 3 silent gives about 0.208 to 0.939.
Run: python -m unittest discover -s tests -p "test_deep*.py" -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))

from uncertainty import build_report, wilson  # noqa: E402


class WilsonTests(unittest.TestCase):
    def test_repair_rate_interval(self):
        lo, hi = wilson(3, 8)
        self.assertAlmostEqual(lo, 0.1369, places=3)
        self.assertAlmostEqual(hi, 0.6943, places=3)

    def test_silent_failure_rate_interval(self):
        lo, hi = wilson(2, 3)
        self.assertAlmostEqual(lo, 0.2077, places=3)
        self.assertAlmostEqual(hi, 0.9385, places=3)

    def test_all_successes_keeps_upper_bound_at_one(self):
        lo, hi = wilson(8, 8)
        self.assertAlmostEqual(hi, 1.0)
        self.assertLess(lo, 0.7)

    def test_zero_trials_is_rejected(self):
        with self.assertRaises(ValueError):
            wilson(0, 0)


class ReportTests(unittest.TestCase):
    def test_committed_report_matches_a_fresh_build(self):
        with open(os.path.join(ROOT, "level-3-deep", "uncertainty.json"), encoding="utf-8") as fh:
            committed = json.load(fh)
        self.assertEqual(committed, build_report())

    def test_report_counts_come_from_the_results_files(self):
        report = build_report()
        self.assertEqual(report["repair_rate"]["successes"], 3)
        self.assertEqual(report["repair_rate"]["trials"], 8)
        self.assertEqual(report["silent_failure_rate"]["successes"], 2)
        self.assertEqual(report["silent_failure_rate"]["trials"], 3)


if __name__ == "__main__":
    unittest.main()

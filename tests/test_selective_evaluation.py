import unittest
import numpy as np
from selective_evaluation import confidence_report, wilson_interval


class SelectiveEvaluationTests(unittest.TestCase):
    def test_empty_subset_is_explicit(self):
        r = confidence_report([1, 0], [.6, .4], thresholds=(.8,))["thresholds"][0]
        self.assertEqual(r["selected_bouts"], 0)
        self.assertEqual(r["coverage"], 0)
        self.assertIsNone(r["accuracy"])
        self.assertEqual(r["accuracy_95pct_wilson_interval"], [None, None])

    def test_accuracy_and_coverage(self):
        r = confidence_report([1, 1, 0, 1], [.9, .6, .1, .55],
                              thresholds=(.8,))["thresholds"][0]
        self.assertEqual(r["selected_bouts"], 2)
        self.assertEqual(r["correct_predictions"], 2)
        self.assertAlmostEqual(r["coverage"], .5)
        self.assertEqual(r["accuracy"], 1.0)
        self.assertLess(r["accuracy_95pct_wilson_interval"][0], .8)

    def test_market_same_selected_bouts(self):
        r = confidence_report([1, 0, 1], [.9, .1, .5],
                              market_prob=[.2, .8, np.nan], thresholds=(.8,))["thresholds"][0]
        self.assertEqual(r["same_bouts_market_comparison"]["n"], 2)
        self.assertEqual(r["same_bouts_market_comparison"]["market_accuracy"], 0)
        self.assertEqual(r["same_bouts_market_comparison"]["model_accuracy"], 1)

    def test_wilson_interval(self):
        lo, hi = wilson_interval(80, 100)
        self.assertLess(lo, .8)
        self.assertGreater(hi, .8)

    def test_bad_probability_rejected(self):
        with self.assertRaises(ValueError):
            confidence_report([0], [float("nan")])


if __name__ == "__main__":
    unittest.main()

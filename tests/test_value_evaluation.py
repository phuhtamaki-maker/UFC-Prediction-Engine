import unittest
import numpy as np
from value_evaluation import evaluate_value_bets


class ValueEvaluationTests(unittest.TestCase):
    def test_no_bets_when_prices_missing(self):
        r = evaluate_value_bets([1, 0], [.7, .4], [np.nan, 2.0], [2.5, np.nan])
        self.assertEqual(r["bets"], 0)
        self.assertIsNone(r["realized_roi"])

    def test_profit_and_loss_are_flat_stake(self):
        r = evaluate_value_bets([1, 1], [.7, .7], [2., 2.], [1.5, 1.5])
        self.assertEqual(r["bets"], 2)
        self.assertEqual(r["profit_units"], 2.0)

    def test_losing_bet(self):
        r = evaluate_value_bets([0], [.7], [2.0], [1.5])
        self.assertEqual(r["profit_units"], -1)
        self.assertEqual(r["realized_roi"], -1)

    def test_no_edge_means_no_bet(self):
        r = evaluate_value_bets([1], [.5], [1.8], [1.8])
        self.assertEqual(r["bets"], 0)

    def test_invalid_probabilities_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_value_bets([1], [1.2], [2.0], [2.0])

    def test_one_side_missing_never_bets(self):
        r = evaluate_value_bets([1], [.8], [2.0], [np.nan])
        self.assertEqual(r["bets"], 0)


if __name__ == "__main__":
    unittest.main()

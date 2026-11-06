import unittest
import numpy as np
from market_blend import mix_probabilities, fit_model_weight


class MarketBlendTests(unittest.TestCase):
    def test_symmetric_under_fighter_switch(self):
        p = np.array([0.2, 0.8, 0.55])
        q = np.array([0.3, 0.7, 0.45])
        for w in [0, .25, .5, 1]:
            np.testing.assert_allclose(
                mix_probabilities(p, q, w),
                1 - mix_probabilities(1 - p, 1 - q, w), atol=1e-12)

    def test_missing_market_odds_falls_back_to_model(self):
        x = mix_probabilities(np.array([.6, .7]), np.array([float("nan"), .4]), .5)
        self.assertAlmostEqual(x[0], .6)
        self.assertAlmostEqual(x[1], .55)

    def test_validation_can_choose_market_when_it_is_correct(self):
        y = np.array([0, 1] * 30)
        market = np.array([.1, .9] * 30)
        model = np.array([.9, .1] * 30)
        selected = fit_model_weight(y, model, market)
        self.assertEqual(selected["validation_n"], 60)
        self.assertEqual(selected["model_weight"], 0)

    def test_missing_data_does_not_optimize_weight(self):
        y = np.array([0, 1] * 30)
        market = np.array([float("nan")] * 60)
        model = np.array([.4, .6] * 30)
        selected = fit_model_weight(y, model, market)
        self.assertEqual(selected["validation_n"], 0)
        self.assertEqual(selected["model_weight"], 0)


if __name__ == "__main__":
    unittest.main()

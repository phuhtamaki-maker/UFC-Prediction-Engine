import unittest
import pandas as pd
from data_quality import safe_pairwise, row_features, SAFE_FEATURES
from engine import FEATURES, prepared_rows


class MissingPhysicalDataTests(unittest.TestCase):
    def test_missing_side_neutral_not_zero_age(self):
        diff, available = safe_pairwise({"f1_age": 32, "f2_age": None}, "age")
        self.assertEqual((diff, available), (0.0, 0))

    def test_both_valid_difference(self):
        self.assertEqual(safe_pairwise({"f1_age": 32, "f2_age": 27}, "age"), (5.0, 1))
        self.assertEqual(safe_pairwise({"f1_reach_cm": 190, "f2_reach_cm": 180}, "reach_cm"), (10.0, 1))

    def test_invalid_anthropometrics_neutral(self):
        self.assertEqual(safe_pairwise({"f1_height_cm": 0, "f2_height_cm": 183}, "height_cm"), (0., 0))

    def test_swap_antisymmetric(self):
        for name in ("age", "reach_cm", "height_cm"):
            a = {"age": 29., "reach_cm": 184., "height_cm": 176.}[name]
            b = {"age": 31., "reach_cm": 193., "height_cm": 182.}[name]
            one, _ = safe_pairwise({"f1_"+name:a, "f2_"+name:b}, name)
            opposite, _ = safe_pairwise({"f1_"+name:b, "f2_"+name:a}, name)
            self.assertEqual(one, -opposite)

    def test_model_remains_old_for_now(self):
        self.assertTrue(all(name not in FEATURES for name in SAFE_FEATURES))

    def test_history_rows_include_research_columns(self):
        data = pd.DataFrame([{"event_date": "2024-02-01", "fight_id": "x",
             "f1_name": "A", "f2_name": "B", "result_f1": "W", "result_f2": "L",
             "f1_age": 27, "f2_age": None}])
        rows, _ = prepared_rows(data)
        self.assertEqual(rows.iloc[0].age_pairwise_diff, 0.)
        self.assertEqual(rows.iloc[0].age_pairwise_diff_available, 0)
        self.assertNotEqual(rows.iloc[0].age_diff, 0.)


if __name__ == "__main__":
    unittest.main()

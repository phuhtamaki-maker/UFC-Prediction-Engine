import unittest
import pandas as pd
from forecast_validation import validate_forecast_rows


def example():
    return pd.DataFrame([{"date": "2026-11-14", "fighter_1": "Alpha",
                          "fighter_2": "Beta", "p_fighter_1": 0.65,
                          "p_fighter_2": 0.35}])


class ForecastValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate_forecast_rows(example()))

    def test_missing_column(self):
        with self.assertRaisesRegex(ValueError, "Missing forecast"):
            validate_forecast_rows(example().drop(columns=["p_fighter_2"]))

    def test_duplicate_reversed_names(self):
        frame = example()
        duplicate = frame.copy()
        duplicate["fighter_1"], duplicate["fighter_2"] = " beta ", " ALPHA "
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_forecast_rows(pd.concat([frame, duplicate], ignore_index=True))

    def test_bad_probability(self):
        frame = example()
        frame.loc[0, "p_fighter_1"] = float("nan")
        with self.assertRaisesRegex(ValueError, "probability"):
            validate_forecast_rows(frame)

    def test_probabilities_not_complementary(self):
        frame = example()
        frame.loc[0, "p_fighter_2"] = 0.4
        with self.assertRaisesRegex(ValueError, "sum to one"):
            validate_forecast_rows(frame)

    def test_same_fighter(self):
        frame = example()
        frame.loc[0, "fighter_2"] = " alpha "
        with self.assertRaisesRegex(ValueError, "fighter names"):
            validate_forecast_rows(frame)

    def test_invalid_date(self):
        frame = example()
        frame.loc[0, "date"] = "not a date"
        with self.assertRaisesRegex(ValueError, "date"):
            validate_forecast_rows(frame)


if __name__ == "__main__":
    unittest.main()

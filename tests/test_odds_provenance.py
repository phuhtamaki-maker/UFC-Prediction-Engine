import unittest
import pandas as pd
from odds_provenance import validate_odds_history


def example():
    return pd.DataFrame([{
        "bout_id": "event-1-fight-1", "event_time": "2025-01-01T20:00:00Z",
        "prediction_time": "2025-01-01T18:00:00Z",
        "odds_time": "2025-01-01T19:00:00Z",
        "model_commit": "abc123", "bookmaker": "sample",
        "fighter1_id": "fighter-a", "fighter2_id": "fighter-b",
        "fighter1_probability": 0.65,
        "fighter1_decimal_odds": 1.8, "fighter2_decimal_odds": 2.1,
        "fighter1_won": 1,
    }])


class OddsProvenanceTests(unittest.TestCase):
    def test_empty_dataset_rejected(self):
        with self.assertRaisesRegex(ValueError, "No historical bouts"):
            validate_odds_history(example().iloc[0:0])

    def test_valid_pre_fight_row(self):
        self.assertEqual(len(validate_odds_history(example())), 1)

    def test_prediction_after_event_rejected(self):
        data = example()
        data.loc[0, "prediction_time"] = "2025-01-01T20:01:00Z"
        with self.assertRaisesRegex(ValueError, "predate"):
            validate_odds_history(data)

    def test_odds_before_prediction_rejected(self):
        data = example()
        data.loc[0, "odds_time"] = "2025-01-01T17:00:00Z"
        with self.assertRaisesRegex(ValueError, "at or after"):
            validate_odds_history(data)

    def test_odds_at_event_rejected(self):
        data = example()
        data.loc[0, "odds_time"] = data.loc[0, "event_time"]
        with self.assertRaisesRegex(ValueError, "predate"):
            validate_odds_history(data)

    def test_missing_timezone_timestamp_rejected(self):
        data = example()
        data.loc[0, "odds_time"] = None
        with self.assertRaisesRegex(ValueError, "odds_time"):
            validate_odds_history(data)

    def test_timezone_naive_timestamps_rejected(self):
        for field in ("event_time", "prediction_time", "odds_time"):
            with self.subTest(field=field):
                data = example()
                data.loc[0, field] = "2025-01-01T19:00:00"
                with self.assertRaisesRegex(ValueError, "timezone-naive"):
                    validate_odds_history(data)

    def test_duplicate_bout_rejected(self):
        data = pd.concat([example(), example()], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_odds_history(data)

    def test_whitespace_duplicate_bout_rejected(self):
        data = pd.concat([example(), example()], ignore_index=True)
        data.loc[1, "bout_id"] = "  event-1-fight-1  "
        with self.assertRaisesRegex(ValueError, "Duplicate bout identity"):
            validate_odds_history(data)

    def test_missing_bookmaker_rejected(self):
        data = example()
        data.loc[0, "bookmaker"] = ""
        with self.assertRaisesRegex(ValueError, "bookmaker"):
            validate_odds_history(data)

    def test_invalid_prices_rejected(self):
        data = example()
        data.loc[0, "fighter2_decimal_odds"] = 1
        with self.assertRaisesRegex(ValueError, "prices"):
            validate_odds_history(data)

    def test_non_binary_outcome_rejected(self):
        data = example()
        data.loc[0, "fighter1_won"] = 2
        with self.assertRaisesRegex(ValueError, "binary"):
            validate_odds_history(data)


if __name__ == "__main__":
    unittest.main()

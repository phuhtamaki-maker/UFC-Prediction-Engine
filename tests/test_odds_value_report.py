import unittest
import pandas as pd

from odds_value_report import build_value_report


def row():
    return {
        "bout_id": "bout-1",
        "event_time": "2025-01-01T20:00:00Z",
        "prediction_time": "2025-01-01T18:00:00Z",
        "odds_time": "2025-01-01T19:00:00Z",
        "model_commit": "abc123",
        "bookmaker": "sample",
        "fighter1_id": "fighter-a",
        "fighter2_id": "fighter-b",
        "fighter1_probability": 0.7,
        "fighter1_decimal_odds": 2.0,
        "fighter2_decimal_odds": 1.5,
        "fighter1_won": 1,
    }


class OddsValueReportTests(unittest.TestCase):
    def test_valid_row_reports_profit(self):
        result = build_value_report(pd.DataFrame([row()]))
        self.assertEqual(result["provenance_checked_rows"], 1)
        self.assertEqual(result["bets"], 1)
        self.assertEqual(result["profit_units"], 1.0)
        self.assertEqual(result["realized_roi"], 1.0)

    def test_no_edge_reports_no_bet(self):
        data = row()
        data["fighter1_probability"] = .5
        data["fighter1_decimal_odds"] = 1.8
        data["fighter2_decimal_odds"] = 1.8
        result = build_value_report(pd.DataFrame([data]))
        self.assertEqual(result["bets"], 0)
        self.assertEqual(result["no_bet_bouts"], 1)
        self.assertIsNone(result["realized_roi"])

    def test_earlier_odds_flagged_as_potentially_stale(self):
        data = row()
        data["odds_time"] = "2025-01-01T17:00:00Z"
        result = build_value_report(pd.DataFrame([data]))
        self.assertEqual(result["odds_recorded_before_prediction"], 1)
        self.assertIn("stale", result["price_timing_warning"])

    def test_post_event_odds_block_report(self):
        data = row()
        data["odds_time"] = "2025-01-01T21:00:00Z"
        with self.assertRaisesRegex(ValueError, "predate"):
            build_value_report(pd.DataFrame([data]))


if __name__ == "__main__":
    unittest.main()

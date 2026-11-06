import unittest
import pandas as pd
from engine import prepared_rows, american_decimal, roi_report


class EngineTests(unittest.TestCase):
    def test_odds(self):
        self.assertAlmostEqual(american_decimal(-200), 1.5)
        self.assertAlmostEqual(american_decimal(150), 2.5)
        self.assertIsNone(american_decimal(None))

    def test_same_day_no_leakage(self):
        fights = pd.DataFrame([
            {"event_date":"2024-01-01","f1_name":"A","f2_name":"B","result_f1":"W","result_f2":"L","fight_id":"a"},
            {"event_date":"2024-01-01","f1_name":"A","f2_name":"C","result_f1":"W","result_f2":"L","fight_id":"b"},
            {"event_date":"2024-02-01","f1_name":"A","f2_name":"D","result_f1":"W","result_f2":"L","fight_id":"c"}])
        data, _ = prepared_rows(fights)
        self.assertEqual(len(data), 3)
        self.assertEqual(data.iloc[0].ufc_fights_diff, 0)
        self.assertEqual(data.iloc[1].ufc_fights_diff, 0)
        self.assertEqual(abs(data.iloc[2].ufc_fights_diff), 2)

    def test_exclude_no_contest(self):
        fights = pd.DataFrame([{"event_date":"2024-01-01","f1_name":"A",
                               "f2_name":"B","result_f1":"NC","result_f2":"NC"}])
        data, _ = prepared_rows(fights)
        self.assertTrue(data.empty)

    def test_one_unit_bet(self):
        bouts = pd.DataFrame([{"f1_open":150,"f2_open":-170,"y":1}])
        result = roi_report(bouts, [0.6])
        self.assertEqual(result["bets"], 1)
        self.assertAlmostEqual(result["profit_units"], 1.5)


if __name__ == "__main__":
    unittest.main()

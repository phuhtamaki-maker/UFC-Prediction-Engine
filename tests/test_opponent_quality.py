import unittest
import pandas as pd
from engine import prepared_rows, snap, empty_state, FEATURES


class OpponentQualityTests(unittest.TestCase):
    def test_new_columns_are_training_features(self):
        self.assertIn("recent_form_diff", FEATURES)
        self.assertIn("opponent_quality_diff", FEATURES)

    def test_new_fighter_gets_neutral_prior_form(self):
        snapshot = snap(empty_state(), pd.Timestamp("2026-01-01").date())
        self.assertEqual(snapshot["recent_form"], .5)
        self.assertEqual(snapshot["opponent_quality"], 0)

    def test_same_day_does_not_leak_into_new_features(self):
        data = pd.DataFrame([
            {"event_date":"2024-01-01","fight_id":"1","f1_name":"A","f2_name":"B",
             "result_f1":"W","result_f2":"L"},
            {"event_date":"2024-01-01","fight_id":"2","f1_name":"A","f2_name":"C",
             "result_f1":"W","result_f2":"L"},
            {"event_date":"2024-02-01","fight_id":"3","f1_name":"A","f2_name":"D",
             "result_f1":"L","result_f2":"W"}])
        frame, states = prepared_rows(data)
        self.assertEqual(len(frame), 3)
        # For same-date bouts neither fighter has any prior UFC activity.
        self.assertEqual(frame.iloc[0]["recent_form_diff"], 0)
        self.assertEqual(frame.iloc[1]["recent_form_diff"], 0)
        self.assertEqual(frame.iloc[0]["opponent_quality_diff"], 0)
        self.assertEqual(frame.iloc[1]["opponent_quality_diff"], 0)
        # On the next event A has two previous wins, so form differs.
        self.assertGreater(abs(frame.iloc[2]["recent_form_diff"]), 0)

    def test_future_outcome_does_not_change_past_row(self):
        fights = pd.DataFrame([
            {"event_date":"2024-01-01","fight_id":"a","f1_name":"A","f2_name":"B",
             "result_f1":"W","result_f2":"L"},
            {"event_date":"2024-02-01","fight_id":"b","f1_name":"A","f2_name":"C",
             "result_f1":"W","result_f2":"L"},
            {"event_date":"2024-03-01","fight_id":"c","f1_name":"A","f2_name":"D",
             "result_f1":"W","result_f2":"L"}])
        first, _ = prepared_rows(fights)
        other = fights.copy()
        other.loc[2, "result_f1"] = "L"
        other.loc[2, "result_f2"] = "W"
        later, _ = prepared_rows(other)
        for col in ("recent_form_diff", "opponent_quality_diff"):
            self.assertEqual(first.iloc[2][col], later.iloc[2][col])


if __name__ == "__main__":
    unittest.main()

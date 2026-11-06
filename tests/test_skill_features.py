import unittest
import pandas as pd
from skill_features import state, snapshot, update
from engine import prepared_rows, FEATURES, SKILL_FEATURES


class SkillProfileTests(unittest.TestCase):
    def test_missing_stats_neutral(self):
        self.assertEqual(snapshot(state())["sig_strikes_per_min"], 3)
        self.assertEqual(snapshot(state())["sig_strike_defense"], .5)
        self.assertEqual(snapshot(state())["takedown_defense"], .5)

    def test_first_bout_not_own_input(self):
        fights = pd.DataFrame([
            {"event_date":"2024-01-01","fight_id":"one","f1_name":"A","f2_name":"B",
             "result_f1":"W","result_f2":"L","fight_duration_sec":300,
             "f1_tot_sig_str_landed":40,"f2_tot_sig_str_landed":1,
             "f1_tot_sig_str_att":45,"f2_tot_sig_str_att":2,
             "f1_tot_td_landed":4,"f2_tot_td_landed":0,
             "f1_tot_td_att":5,"f2_tot_td_att":1},
            {"event_date":"2024-02-01","fight_id":"two","f1_name":"A","f2_name":"C",
             "result_f1":"L","result_f2":"W","fight_duration_sec":300,
             "f1_tot_sig_str_landed":1,"f2_tot_sig_str_landed":60}])
        frame, _ = prepared_rows(fights)
        self.assertEqual(frame.iloc[0]["sig_strikes_per_min_diff"], 0)
        self.assertEqual(frame.iloc[0]["takedowns_per_15min_diff"], 0)
        self.assertNotEqual(frame.iloc[1]["sig_strikes_per_min_diff"], 0)
        self.assertNotEqual(frame.iloc[1]["takedowns_per_15min_diff"], 0)

    def test_same_day_no_stats_leak(self):
        fights = pd.DataFrame([
            {"event_date":"2024-01-01","fight_id":"a","f1_name":"A","f2_name":"B",
             "result_f1":"W","result_f2":"L","fight_duration_sec":300,
             "f1_tot_sig_str_landed":80,"f2_tot_sig_str_landed":2},
            {"event_date":"2024-01-01","fight_id":"b","f1_name":"A","f2_name":"C",
             "result_f1":"W","result_f2":"L","fight_duration_sec":300,
             "f1_tot_sig_str_landed":20,"f2_tot_sig_str_landed":2}])
        frame, _ = prepared_rows(fights)
        self.assertEqual(frame.iloc[0]["sig_strikes_per_min_diff"], 0)
        self.assertEqual(frame.iloc[1]["sig_strikes_per_min_diff"], 0)

    def test_target_bout_stats_change_cannot_affect_own_profile(self):
        fights = pd.DataFrame([
            {"event_date":"2024-01-01","fight_id":"a","f1_name":"A","f2_name":"B",
             "result_f1":"W","result_f2":"L","fight_duration_sec":300,
             "f1_tot_sig_str_landed":80,"f2_tot_sig_str_landed":2},
            {"event_date":"2024-02-01","fight_id":"b","f1_name":"A","f2_name":"C",
             "result_f1":"W","result_f2":"L","fight_duration_sec":300,
             "f1_tot_sig_str_landed":20,"f2_tot_sig_str_landed":2}])
        before, _ = prepared_rows(fights)
        modified = fights.copy()
        modified.loc[1, "f1_tot_sig_str_landed"] = 200
        after, _ = prepared_rows(modified)
        for col in SKILL_FEATURES:
            self.assertEqual(before.iloc[1][col], after.iloc[1][col])

    def test_not_enabled_by_default(self):
        self.assertTrue(all(name not in FEATURES for name in SKILL_FEATURES))


if __name__ == "__main__":
    unittest.main()

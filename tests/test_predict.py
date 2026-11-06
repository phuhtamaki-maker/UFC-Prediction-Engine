import unittest
import pandas as pd
from predict import run_predictions


class UpcomingTests(unittest.TestCase):
    @staticmethod
    def historical():
        fighters = ["A", "B", "C", "D", "E", "F"]
        bouts = []
        for i in range(1, 31):
            a = fighters[i % 6]
            b = fighters[(i + 2) % 6]
            bouts.append({"event_date": f"2024-01-{i:02d}",
                          "f1_name":a, "f2_name":b,
                          "f1_id":"id"+a, "f2_id":"id"+b,
                          "result_f1":"W" if i%2 else "L",
                          "result_f2":"L" if i%2 else "W"})
        return pd.DataFrame(bouts)

    def test_probabilities_sum_to_one(self):
        card = pd.DataFrame([
            {"event_date":"2024-02-01","f1_name":"A","f2_name":"C"},
            {"event_date":"2024-02-01","f1_name":"C","f2_name":"A"}])
        predictions = run_predictions(self.historical(), card)
        self.assertAlmostEqual(predictions.iloc[0].p_fighter_1 +
                               predictions.iloc[1].p_fighter_1, 1, places=3)

    def test_future_results_are_excluded(self):
        past = self.historical()
        card = pd.DataFrame([{"event_date":"2024-02-01","f1_name":"A","f2_name":"C"}])
        baseline = run_predictions(past, card).iloc[0].p_fighter_1
        leaked = past.iloc[:1].copy()
        leaked["event_date"] = "2024-02-01"
        changed = run_predictions(pd.concat([past, leaked]), card).iloc[0].p_fighter_1
        self.assertEqual(baseline, changed)

    def test_unknown_fighter_warns(self):
        card = pd.DataFrame([{"event_date":"2024-02-01","f1_name":"A","f2_name":"Newbie"}])
        predictions = run_predictions(self.historical(), card)
        self.assertEqual(predictions.iloc[0].warning, "Limited UFC history")


if __name__ == "__main__":
    unittest.main()

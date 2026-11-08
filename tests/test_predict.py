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

    def test_empty_card_rejected(self):
        card = pd.DataFrame(columns=["event_date", "f1_name", "f2_name"])
        with self.assertRaisesRegex(ValueError, "at least one bout"):
            run_predictions(self.historical(), card)

    def test_missing_fighter_name_rejected(self):
        for bad_name in (None, float("nan"), "  "):
            with self.subTest(name=bad_name):
                card = pd.DataFrame([{"event_date": "2024-02-01",
                                      "f1_name": "A", "f2_name": bad_name}])
                with self.assertRaisesRegex(ValueError, "two different names"):
                    run_predictions(self.historical(), card)

    def test_probabilities_sum_to_one(self):
        card = pd.DataFrame([
            {"event_date":"2024-02-01","f1_name":"A","f2_name":"C"},
            {"event_date":"2024-02-01","f1_name":"B","f2_name":"D"}])
        predictions = run_predictions(self.historical(), card)
        for _, row in predictions.iterrows():
            self.assertAlmostEqual(row.p_fighter_1 + row.p_fighter_2, 1, places=3)

    def test_duplicate_reversed_bout_is_rejected(self):
        card = pd.DataFrame([
            {"event_date":"2024-02-01","f1_name":"A","f2_name":"C"},
            {"event_date":"2024-02-01","f1_name":"C","f2_name":"A"}])
        with self.assertRaisesRegex(ValueError, "Duplicate forecast bout"):
            run_predictions(self.historical(), card)

    def test_future_results_are_excluded(self):
        past = self.historical()
        card = pd.DataFrame([{"event_date":"2024-02-01","f1_name":"A","f2_name":"C"}])
        baseline = run_predictions(past, card).iloc[0].p_fighter_1
        leaked = past.iloc[:1].copy()
        leaked["event_date"] = "2024-02-01"
        changed = run_predictions(pd.concat([past, leaked]), card).iloc[0].p_fighter_1
        self.assertEqual(baseline, changed)

    def test_ambiguous_historical_name_is_rejected(self):
        history = self.historical()
        duplicate = history.iloc[[0]].copy()
        duplicate["event_date"] = "2024-01-31"
        duplicate["f1_name"] = "A"
        duplicate["f1_id"] = "different-id-for-A"
        history = pd.concat([history, duplicate], ignore_index=True)
        card = pd.DataFrame([{"event_date": "2024-02-01",
                             "f1_name": "A", "f2_name": "C"}])
        with self.assertRaisesRegex(ValueError, "Ambiguous historical fighter identity"):
            run_predictions(history, card)

    def test_unrelated_ambiguous_name_does_not_block_card(self):
        history = self.historical()
        duplicate = history.iloc[[0]].copy()
        duplicate["event_date"] = "2024-01-31"
        duplicate["f1_name"] = "B"
        duplicate["f1_id"] = "different-id-for-B"
        history = pd.concat([history, duplicate], ignore_index=True)
        card = pd.DataFrame([{"event_date": "2024-02-01",
                             "f1_name": "A", "f2_name": "C"}])
        self.assertEqual(len(run_predictions(history, card)), 1)

    def test_repeated_same_fighter_id_is_allowed(self):
        history = self.historical()
        repeated = history.iloc[[0]].copy()
        repeated["event_date"] = "2024-01-31"
        history = pd.concat([history, repeated], ignore_index=True)
        card = pd.DataFrame([{"event_date": "2024-02-01",
                             "f1_name": "A", "f2_name": "C"}])
        self.assertEqual(len(run_predictions(history, card)), 1)

    def test_unknown_fighter_warns(self):
        card = pd.DataFrame([{"event_date":"2024-02-01","f1_name":"A","f2_name":"Newbie"}])
        predictions = run_predictions(self.historical(), card)
        self.assertEqual(predictions.iloc[0].warning, "Limited UFC history")


if __name__ == "__main__":
    unittest.main()

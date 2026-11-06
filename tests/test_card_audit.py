import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from card_audit import audit_card
from score_frozen import file_sha256


class CardAuditTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        folder = Path(self.workspace.name)
        self.frozen = folder / "frozen.csv"
        self.manifest = folder / "manifest.json"
        self.card = folder / "card.csv"
        pd.DataFrame([
            {"date": "2026-11-07", "fighter_1": "A", "fighter_2": "B",
             "p_fighter_1": 0.7, "p_fighter_2": 0.3},
            {"date": "2026-11-07", "fighter_1": "C", "fighter_2": "D",
             "p_fighter_1": 0.5, "p_fighter_2": 0.5},
        ]).to_csv(self.frozen, index=False)
        self.manifest.write_text(json.dumps({"prediction_count": 2,
                                              "predictions_sha256": file_sha256(self.frozen)}))
        self.write_card([("B", "A"), ("C", "D")])

    def tearDown(self):
        self.workspace.cleanup()

    def write_card(self, pairs):
        pd.DataFrame([{"event_date": "2026-11-07", "f1_name": a, "f2_name": b}
                      for a, b in pairs]).to_csv(self.card, index=False)

    def test_reversed_order_same_card(self):
        result = audit_card(self.frozen, self.manifest, self.card)
        self.assertEqual(result["unchanged"], 2)
        self.assertEqual(result["possible_opponent_change"], 0)

    def test_possible_replacement_not_counted_as_loss(self):
        self.write_card([("A", "X"), ("C", "D")])
        result = audit_card(self.frozen, self.manifest, self.card)
        self.assertEqual(result["possible_opponent_change"], 1)
        self.assertEqual(result["unchanged"], 1)
        self.assertEqual(result["frozen_bouts"][0]["status"], "possible_opponent_change")
        self.assertNotIn("accuracy", result)

    def test_missing_pair_not_assumed_cancelled(self):
        self.write_card([("C", "D")])
        result = audit_card(self.frozen, self.manifest, self.card)
        self.assertEqual(result["not_listed"], 1)
        self.assertEqual(result["frozen_bouts"][0]["status"], "not_listed")

    def test_tampered_forecast_detected(self):
        self.frozen.write_text(self.frozen.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            audit_card(self.frozen, self.manifest, self.card)

    def test_duplicate_current_match_rejected(self):
        self.write_card([("B", "A"), ("A", "B")])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit_card(self.frozen, self.manifest, self.card)


if __name__ == "__main__":
    unittest.main()

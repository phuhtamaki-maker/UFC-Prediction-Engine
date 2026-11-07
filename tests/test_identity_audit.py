import unittest

import pandas as pd

from identity_audit import audit_identities
from engine import fighter_key


class FighterIdentityAuditTests(unittest.TestCase):
    def test_counts_only_pre_cutoff_collisions(self):
        data = pd.DataFrame([
            {"event_date": "2024-01-01", "f1_name": "Alex", "f1_id": "one",
             "f2_name": "Bob", "f2_id": "bob"},
            {"event_date": "2024-02-01", "f1_name": " ALEX ", "f1_id": "two",
             "f2_name": "Bob", "f2_id": "bob"},
            {"event_date": "2025-01-01", "f1_name": "Bob", "f1_id": "other-bob",
             "f2_name": "Alex", "f2_id": "two"},
        ])
        report = audit_identities(data, "2025-01-01")
        self.assertEqual(report["historical_bouts"], 2)
        self.assertEqual(report["ambiguous_names"], 1)
        self.assertEqual(report["ambiguous_name_ids"], {"alex": ["one", "two"]})
        self.assertEqual(report["ambiguous_name_occurrences"],
                         {"alex": {"one": 1, "two": 1}})

    def test_invalid_dates_are_excluded(self):
        data = pd.DataFrame([
            {"event_date": "not-a-date", "f1_name": "Alex", "f1_id": "bad",
             "f2_name": "Bob", "f2_id": "bob"},
            {"event_date": "2024-01-01", "f1_name": "Alex", "f1_id": "good",
             "f2_name": "Bob", "f2_id": "bob"},
        ])
        report = audit_identities(data)
        self.assertEqual(report["invalid_date_rows_excluded"], 1)
        self.assertEqual(report["ambiguous_names"], 0)
        self.assertEqual(report["ambiguous_name_occurrences"], {})

    def test_repeated_same_id_is_not_ambiguous(self):
        data = pd.DataFrame([
            {"event_date": "2024-01-01", "f1_name": "Bruno Silva", "f1_id": "fighter-a",
             "f2_name": "Opponent", "f2_id": "opponent"},
            {"event_date": "2024-02-01", "f1_name": " BRUNO  SILVA ", "f1_id": "fighter-a",
             "f2_name": "Opponent", "f2_id": "opponent"},
        ])
        report = audit_identities(data)
        self.assertEqual(report["ambiguous_names"], 0)
        self.assertEqual(report["unique_normalized_names"], 2)

    def test_missing_id_and_explicit_id_are_flagged_for_review(self):
        data = pd.DataFrame([
            {"event_date": "2024-01-01", "f1_name": "Bruno Silva", "f1_id": None,
             "f2_name": "Opponent", "f2_id": "opponent"},
            {"event_date": "2024-02-01", "f1_name": "Bruno Silva", "f1_id": "fighter-a",
             "f2_name": "Opponent", "f2_id": "opponent"},
        ])
        report = audit_identities(data)
        self.assertEqual(report["ambiguous_name_ids"], {"bruno silva": ["bruno silva", "fighter-a"]})
        self.assertEqual(report["ambiguous_name_occurrences"],
                         {"bruno silva": {"bruno silva": 1, "fighter-a": 1}})

    def test_fighter_key_handles_missing_id_markers(self):
        for missing in (None, float("nan"), "", "None", "null", "<NA>"):
            with self.subTest(missing=repr(missing)):
                row = pd.Series({"f1_name": " Bruno  Silva ", "f1_id": missing})
                self.assertEqual(fighter_key(row, 1), "bruno silva")

    def test_fighter_key_preserves_real_id(self):
        row = pd.Series({"f1_name": "Bruno Silva", "f1_id": "fighter-a"})
        self.assertEqual(fighter_key(row, 1), "fighter-a")

    def test_missing_columns_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            audit_identities(pd.DataFrame({"event_date": ["2024-01-01"]}))


if __name__ == "__main__":
    unittest.main()

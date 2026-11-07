import unittest

import pandas as pd

from identity_audit import audit_identities


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

    def test_missing_columns_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            audit_identities(pd.DataFrame({"event_date": ["2024-01-01"]}))


if __name__ == "__main__":
    unittest.main()

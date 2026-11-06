import unittest
import pandas as pd

from physical_data_audit import audit


def fight(date, result=("W", "L"), age=(30, 27), reach=(190, 180),
          height=(180, 175)):
    row = {"event_date": date, "result_f1": result[0], "result_f2": result[1]}
    for field, values in (("age", age), ("reach_cm", reach), ("height_cm", height)):
        row["f1_" + field], row["f2_" + field] = values
    return row


class PhysicalDataCoverageAuditTests(unittest.TestCase):
    def test_counts_valid_one_missing_and_neither_by_year(self):
        rows = [
            fight("2024-01-01"),
            fight("2024-02-01", age=(30, None), reach=(None, None)),
            fight("2025-01-01", age=(0, 31), height=(None, None)),
        ]
        report = audit(pd.DataFrame(rows))
        self.assertEqual(report["overall"]["fights"], 3)
        self.assertEqual(report["overall"]["age"], {
            "both_valid": 1, "one_valid": 2, "neither_valid": 0,
            "both_valid_pct": 33.33,
        })
        self.assertEqual(report["by_year"]["2024"]["reach_cm"]["neither_valid"], 1)
        self.assertEqual(report["by_year"]["2025"]["height_cm"]["neither_valid"], 1)

    def test_excludes_undated_and_non_decisive(self):
        rows = [fight("2024-01-01"), fight("not-a-date"),
                fight("2024-01-02", result=("D", "D"))]
        self.assertEqual(audit(pd.DataFrame(rows))["overall"]["fights"], 1)

    def test_empty_valid_set(self):
        report = audit(pd.DataFrame([fight("invalid")]))
        self.assertEqual(report["overall"]["fights"], 0)
        self.assertIsNone(report["overall"]["age"]["both_valid_pct"])

    def test_requires_attributes(self):
        with self.assertRaisesRegex(ValueError, "f1_age"):
            audit(pd.DataFrame([{"event_date": "2024-01-01",
                                "result_f1": "W", "result_f2": "L"}]))


if __name__ == "__main__":
    unittest.main()

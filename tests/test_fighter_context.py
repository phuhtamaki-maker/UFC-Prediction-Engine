import csv
import tempfile
import unittest
from pathlib import Path
from fighter_context import parse_date, verified_observations


class PublicContextDateTests(unittest.TestCase):
    def test_exact_date(self):
        self.assertEqual(parse_date("2026-11-06").isoformat(), "2026-11-06")

    def test_offset_converted_to_utc(self):
        self.assertEqual(parse_date("2026-11-07T00:30:00+02:00").isoformat(), "2026-11-06")

    def test_malformed_suffix_rejected(self):
        with self.assertRaises(ValueError):
            parse_date("2026-11-06THIS_IS_NOT_A_TIMESTAMP")

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            parse_date("2026-11-06T23:59:00")

    def test_post_event_observation_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "observations.csv"
            with file.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "fighter", "category", "published_date", "source_url",
                    "source_type", "note"])
                writer.writeheader()
                for day in ("2026-11-06T23:00:00Z", "2026-11-07T00:01:00Z"):
                    writer.writerow({"fighter": "Fighter A", "category": "official_weigh_in",
                                     "published_date": day,
                                     "source_url": "https://www.ufc.com/news/example",
                                     "source_type": "ufc", "note": "Public report"})
            rows = verified_observations(file, "2026-11-07")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["published_date"], "2026-11-06T23:00:00Z")


if __name__ == "__main__":
    unittest.main()

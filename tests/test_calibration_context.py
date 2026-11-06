import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np
from calibration import apply_temperature, fit_temperature
from fighter_context import verified_observations


class CalibrationAndEvidenceTests(unittest.TestCase):
    def test_calibration_symmetry(self):
        x = np.array([0.2, 0.3, 0.7, 0.8])
        for t in (0.5, 1.0, 1.6, 3.2):
            np.testing.assert_allclose(apply_temperature(x, t),
                                       1 - apply_temperature(1 - x, t), atol=1e-12)

    def test_temperature_fitted_without_test_outcomes(self):
        probabilities = np.array([.2, .8] * 30)
        outcomes = np.array([0, 1] * 30)
        t = fit_temperature(probabilities, outcomes)
        self.assertGreater(t, 0)
        with self.assertRaises(ValueError):
            fit_temperature(probabilities[:10], outcomes[:10])

    def test_evidence_excludes_late_news_and_unapproved_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "context.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "fighter", "category", "published_date", "source_url", "source_type", "note"])
                writer.writeheader()
                writer.writerow(dict(fighter="Example", category="short_notice",
                    published_date="2026-11-01", source_url="https://ufc.com/example",
                    source_type="ufc", note="Publicly confirmed"))
                writer.writerow(dict(fighter="Example", category="short_notice",
                    published_date="2026-11-09", source_url="https://ufc.com/example",
                    source_type="ufc", note="This must not leak"))
                writer.writerow(dict(fighter="Example", category="public_injury_announcement",
                    published_date="2026-11-01", source_url="https://rumors.example/item",
                    source_type="rumor", note="Unverified"))
            rows = verified_observations(path, "2026-11-07")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["category"], "short_notice")


if __name__ == "__main__":
    unittest.main()

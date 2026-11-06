import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
from score_frozen import score, file_sha256


class FrozenScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        folder = Path(self.temp.name)
        self.frozen = folder / "frozen.csv"
        self.manifest = folder / "manifest.json"
        self.results = folder / "results.csv"
        pd.DataFrame([
            dict(date="2026-11-07", fighter_1="Fighter A", fighter_2="Fighter B",
                 p_fighter_1=.75, p_fighter_2=.25),
            dict(date="2026-11-07", fighter_1="Fighter C", fighter_2="Fighter D",
                 p_fighter_1=.40, p_fighter_2=.60),
            dict(date="2026-11-07", fighter_1="Fighter E", fighter_2="Fighter F",
                 p_fighter_1=.55, p_fighter_2=.45)
        ]).to_csv(self.frozen, index=False)
        self.manifest.write_text(json.dumps({
            "prediction_count": 3, "predictions_sha256": file_sha256(self.frozen),
            "github_run_id": "test-run"}))
        pd.DataFrame([
            dict(event_date="2026-11-07", f1_name="Fighter B",
                 f2_name="Fighter A", result_f1="L", result_f2="W"),
            dict(event_date="2026-11-07", f1_name="Fighter C",
                 f2_name="Fighter D", result_f1="NC", result_f2="NC")
        ]).to_csv(self.results, index=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_reversed_fighter_order_and_unmatched(self):
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["total_frozen"], 3)
        self.assertEqual(result["completed_scored"], 1)
        self.assertEqual(result["correct"], 1)
        self.assertAlmostEqual(result["accuracy"], 1)
        self.assertEqual(result["excluded_or_unmatched"], 2)
        self.assertEqual([r["status"] for r in result["fights"]],
                         ["scored", "non_decisive_or_not_complete", "unmatched"])

    def test_tampering_detected(self):
        self.frozen.write_text(self.frozen.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            score(self.frozen, self.manifest, self.results)

    def test_duplicated_result_not_scored(self):
        df = pd.read_csv(self.results)
        df = pd.concat([df, df.iloc[:1]], ignore_index=True)
        df.to_csv(self.results, index=False)
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["completed_scored"], 0)
        self.assertEqual(result["fights"][0]["status"], "ambiguous_duplicate_result")

    def test_invalid_probability_rejected(self):
        df = pd.read_csv(self.frozen)
        df.loc[0, "p_fighter_1"] = .90
        df.to_csv(self.frozen, index=False)
        self.manifest.write_text(json.dumps({
            "prediction_count": 3, "predictions_sha256": file_sha256(self.frozen)}))
        with self.assertRaisesRegex(ValueError, "probabilities"):
            score(self.frozen, self.manifest, self.results)


if __name__ == "__main__":
    unittest.main()

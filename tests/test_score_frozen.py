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

    def test_uncertainty_and_confidence_report_use_scored_only(self):
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["accuracy_95pct_wilson_interval"], [0.2065, 1.0])
        rows = result["confidence_diagnostics"]["thresholds"]
        self.assertEqual([row["selected_bouts"] for row in rows], [1, 1, 0])
        self.assertEqual(rows[0]["total_bouts"], 1)
        self.assertEqual(rows[0]["correct_predictions"], 1)
        self.assertIsNone(rows[2]["accuracy"])

    def test_no_scored_fights_has_no_misleading_accuracy(self):
        pd.DataFrame(columns=["event_date", "f1_name", "f2_name",
                              "result_f1", "result_f2"]).to_csv(self.results, index=False)
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["completed_scored"], 0)
        self.assertIsNone(result["accuracy"])
        self.assertEqual(result["accuracy_95pct_wilson_interval"], [None, None])
        self.assertTrue(all(x["selected_bouts"] == 0
                            for x in result["confidence_diagnostics"]["thresholds"]))

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

    def test_rejects_forged_post_cutoff_snapshot(self):
        data = json.loads(self.manifest.read_text())
        data["generated_utc"] = "2026-11-07T13:00:00Z"
        data["cutoff_utc"] = "2026-11-07T12:00:00Z"
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Post-cutoff"):
            score(self.frozen, self.manifest, self.results)

    def test_rejects_fight_before_cutoff_date(self):
        data = json.loads(self.manifest.read_text())
        data["generated_utc"] = "2026-11-06T21:00:00Z"
        data["cutoff_utc"] = "2026-11-08T12:00:00Z"
        self.manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "before UTC cutoff"):
            score(self.frozen, self.manifest, self.results)

    def test_valid_manifest_chronology_is_checked(self):
        data = json.loads(self.manifest.read_text())
        data["generated_utc"] = "2026-11-06T21:00:00Z"
        data["cutoff_utc"] = "2026-11-07T12:00:00Z"
        self.manifest.write_text(json.dumps(data))
        result = score(self.frozen, self.manifest, self.results)
        self.assertTrue(result["snapshot_chronology_checked"])

    def test_exact_fifty_fifty_is_no_directional_pick(self):
        df = pd.read_csv(self.frozen)
        df.loc[0, ["p_fighter_1", "p_fighter_2"]] = [0.5, 0.5]
        df.to_csv(self.frozen, index=False)
        data = json.loads(self.manifest.read_text())
        data["predictions_sha256"] = file_sha256(self.frozen)
        self.manifest.write_text(json.dumps(data))
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["completed_scored"], 1)
        self.assertEqual(result["directional_picks"], 0)
        self.assertEqual(result["ties"], 1)
        self.assertEqual(result["correct"], 0)
        self.assertIsNone(result["accuracy"])
        self.assertEqual(result["accuracy_95pct_wilson_interval"], [None, None])
        self.assertEqual(result["fights"][0]["winner_pick"], "no_pick")
        self.assertAlmostEqual(result["brier"], 0.25)
        self.assertAlmostEqual(result["log_loss"], 0.6931)

    def test_fifty_fifty_reversed_order_stays_no_pick(self):
        df = pd.read_csv(self.frozen)
        df.loc[0, ["fighter_1", "fighter_2"]] = ["Fighter B", "Fighter A"]
        df.loc[0, ["p_fighter_1", "p_fighter_2"]] = [0.5, 0.5]
        df.to_csv(self.frozen, index=False)
        data = json.loads(self.manifest.read_text())
        data["predictions_sha256"] = file_sha256(self.frozen)
        self.manifest.write_text(json.dumps(data))
        result = score(self.frozen, self.manifest, self.results)
        self.assertEqual(result["directional_picks"], 0)
        self.assertEqual(result["ties"], 1)
        self.assertIsNone(result["accuracy"])

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

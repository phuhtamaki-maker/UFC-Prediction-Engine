import unittest

from archive_validation import validate_archive_metadata


def valid():
    return {
        "created_at_utc": "2026-11-07T17:00:00Z",
        "first_bout_at_utc": "2026-11-07T20:00:00+00:00",
        "training_data_cutoff_utc": "2026-11-06T00:00:00Z",
        "model_commit": "a" * 40,
        "source_sha256": "b" * 64,
        "card_sha256": "c" * 64,
        "predictions_sha256": "d" * 64,
        "command": "python predict.py --card data/upcoming.csv",
        "archive_reference": "git:example",
        "model_features": ["elo_diff", "age_diff"],
    }


class ArchiveValidationTests(unittest.TestCase):
    def test_valid_metadata(self):
        self.assertTrue(validate_archive_metadata(valid()))

    def test_missing_reference(self):
        data = valid()
        del data["archive_reference"]
        with self.assertRaisesRegex(ValueError, "archive_reference"):
            validate_archive_metadata(data)

    def test_naive_timestamp_rejected(self):
        data = valid()
        data["created_at_utc"] = "2026-11-07T17:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            validate_archive_metadata(data)

    def test_after_event_rejected(self):
        data = valid()
        data["created_at_utc"] = "2026-11-07T21:00:00Z"
        with self.assertRaisesRegex(ValueError, "precede"):
            validate_archive_metadata(data)

    def test_future_training_cutoff_rejected(self):
        data = valid()
        data["training_data_cutoff_utc"] = "2026-11-07T19:00:00Z"
        with self.assertRaisesRegex(ValueError, "Training cutoff"):
            validate_archive_metadata(data)

    def test_bad_hash_rejected(self):
        data = valid()
        data["predictions_sha256"] = "unknown"
        with self.assertRaisesRegex(ValueError, "predictions_sha256"):
            validate_archive_metadata(data)

    def test_padded_feature_name_rejected(self):
        data = valid()
        data["model_features"] = ["elo_diff", " age_diff "]
        with self.assertRaisesRegex(ValueError, "model_features"):
            validate_archive_metadata(data)

    def test_whitespace_alias_duplicate_rejected(self):
        data = valid()
        data["model_features"] = ["elo_diff", " elo_diff "]
        with self.assertRaisesRegex(ValueError, "model_features"):
            validate_archive_metadata(data)

    def test_duplicate_features_rejected(self):
        data = valid()
        data["model_features"] = ["elo_diff", "elo_diff"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_archive_metadata(data)


if __name__ == "__main__":
    unittest.main()

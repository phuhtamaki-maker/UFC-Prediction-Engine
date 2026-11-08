"""Strict metadata checks for an independently timestamped pre-event forecast archive.

Passing validation does not establish that the archive was published before the event.
"""
from datetime import datetime, timezone
import re

_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
_REQUIRED = ("created_at_utc", "first_bout_at_utc", "model_commit",
             "training_data_cutoff_utc", "source_sha256", "card_sha256",
             "predictions_sha256", "command", "archive_reference")


def _utc(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing {field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_archive_metadata(metadata):
    """Reject missing, malformed or temporally impossible provenance fields."""
    if not isinstance(metadata, dict):
        raise ValueError("Archive metadata must be an object")
    for field in _REQUIRED:
        if field not in metadata or not isinstance(metadata[field], str) or not metadata[field].strip():
            raise ValueError(f"Missing {field}")
    created = _utc(metadata["created_at_utc"], "created_at_utc")
    first = _utc(metadata["first_bout_at_utc"], "first_bout_at_utc")
    cutoff = _utc(metadata["training_data_cutoff_utc"], "training_data_cutoff_utc")
    if created >= first:
        raise ValueError("Archive creation must precede first bout")
    if cutoff > created:
        raise ValueError("Training cutoff cannot be after archive creation")
    if not _COMMIT.fullmatch(metadata["model_commit"]):
        raise ValueError("Invalid model_commit SHA")
    for field in ("source_sha256", "card_sha256", "predictions_sha256"):
        if not _SHA256.fullmatch(metadata[field]):
            raise ValueError(f"Invalid {field}")
    if not isinstance(metadata.get("model_features"), list) or not metadata["model_features"]:
        raise ValueError("Missing model_features")
    if any(not isinstance(item, str) or not item.strip() or item != item.strip()\n           for item in metadata["model_features"]):
        raise ValueError("Invalid model_features")
    if len(set(metadata["model_features"])) != len(metadata["model_features"]):
        raise ValueError("Duplicate model_features")
    return True

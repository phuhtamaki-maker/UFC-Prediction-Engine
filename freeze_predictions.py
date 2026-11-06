"""Freeze UFC forecast outputs BEFORE a conservative, explicitly set cutoff.

The run's GitHub Actions artifact and logs provide a server timestamp and
commit provenance. This isn't a cryptographic proof of availability of every
upstream data field. Never use a post-event execution as a pre-event forecast.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import pandas as pd
from predict import run_predictions


UTC = dt.timezone.utc


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_cutoff(text):
    value = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("The cutoff must include an explicit timezone")
    return value.astimezone(UTC)


def create_snapshot(history_csv, card_csv, out_dir, cutoff_text, now=None):
    now = now or dt.datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now = now.astimezone(UTC)
    cutoff = parse_cutoff(cutoff_text)
    if now >= cutoff:
        raise ValueError("Forecast cutoff passed: refusing to create a retroactive snapshot")
    if (cutoff - now).total_seconds() > 14 * 24 * 3600:
        raise ValueError("Cutoff is more than 14 days away; wait for a current card")
    card = pd.read_csv(card_csv)
    needed = {"event_date", "f1_name", "f2_name"}
    if not needed <= set(card.columns) or card.empty:
        raise ValueError("Nonempty card must contain event_date, f1_name, f2_name")
    event_dates = pd.to_datetime(card.event_date, errors="coerce")
    if event_dates.isna().any() or (event_dates.dt.date < cutoff.date()).any():
        raise ValueError("Card dates must be at least the cutoff UTC calendar date")
    seen = set()
    for _, fight in card.iterrows():
        names = tuple(sorted((" ".join(str(fight.f1_name).casefold().split()),
                              " ".join(str(fight.f2_name).casefold().split()))))
        if not all(names) or names[0] == names[1] or names in seen:
            raise ValueError("Missing, duplicate, or identical opponent names")
        seen.add(names)
    history = pd.read_csv(history_csv, low_memory=False)
    history_dates = pd.to_datetime(history.event_date, errors="coerce")
    if history_dates.isna().any() or (history_dates.dt.date >= event_dates.min().date()).any():
        raise ValueError("History input contains invalid or target-date/future bouts")
    forecast = run_predictions(history, card)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    snapshot_path = output / "frozen_predictions.csv"
    manifest_path = output / "manifest.json"
    forecast.to_csv(snapshot_path, index=False, float_format="%.4f")
    manifest = {
        "generated_utc": now.isoformat().replace("+00:00", "Z"),
        "cutoff_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "card_sha256": sha256_file(card_csv),
        "historical_data_sha256": sha256_file(history_csv),
        "predictions_sha256": sha256_file(snapshot_path),
        "prediction_count": len(forecast),
        "git_commit": os.environ.get("GITHUB_SHA", "local_unverified"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", "local_unverified"),
        "method": "Existing ten-feature baseline; historic validation-only temperature scaling",
        "limitation": "Fixed predictions, NOT a verified betting edge or a clinical assessment.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", required=True)
    parser.add_argument("--card", required=True)
    parser.add_argument("--cutoff-utc", required=True)
    parser.add_argument("--out", default="results/frozen_card")
    args = parser.parse_args()
    create_snapshot(args.history, args.card, args.out, args.cutoff_utc)


if __name__ == "__main__":
    main()

"""Validate pre-fight provenance before computing research-only value-bet results."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from odds_provenance import validate_odds_history
from value_evaluation import evaluate_value_bets


def build_value_report(frame, min_edge=0.05):
    data = validate_odds_history(frame)
    result = evaluate_value_bets(
        data["fighter1_won"].to_numpy(dtype=int),
        data["fighter1_probability"].to_numpy(dtype=float),
        data["fighter1_decimal_odds"].to_numpy(dtype=float),
        data["fighter2_decimal_odds"].to_numpy(dtype=float),
        min_edge=min_edge,
    )
    result["provenance_checked_rows"] = len(data)
    result["bet_coverage"] = round(result["bets"] / len(data), 4) if len(data) else 0.0
    result["minimum_sample_warning"] = (
        "Small number of bets; realized ROI is highly uncertain and must not "
        "be interpreted as a demonstrated edge."
        if result["bets"] < 100 else None
    )
    result["odds_recorded_before_prediction"] = int((data["odds_time"] < data["prediction_time"]).sum())
    result["price_timing_warning"] = (
        "Odds recorded before prediction may be stale at decision time. "
        "Confirm quoted prices were still executable; timestamp checks alone cannot prove this."
    )
    result["provenance_limit"] = (
        "Timestamps and source fields are supplied by the dataset; this gate "
        "does not independently authenticate their historical availability."
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV of pre-fight predictions and bookmaker prices")
    parser.add_argument("--out", default="results/odds_value_report.json")
    parser.add_argument("--min-edge", type=float, default=0.05)
    args = parser.parse_args()
    report = build_value_report(pd.read_csv(args.input), min_edge=args.min_edge)
    digest = hashlib.sha256()
    with open(args.input, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    report["source_csv_sha256"] = digest.hexdigest()
    report["source_csv_name"] = Path(args.input).name
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

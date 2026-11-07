"""Validate pre-fight provenance before computing research-only value-bet results."""
import argparse
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
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

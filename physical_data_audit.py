"""Research-only audit of pre-fight physical attribute coverage.

No modeling, target labels or post-fight performance inputs are used to
construct the coverage figures. This script does not modify the active model.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from data_quality import FIELDS, valid_measure


def audit(raw):
    required = {"event_date", "result_f1", "result_f2"}
    if not required.issubset(raw.columns):
        raise ValueError("Missing columns: " + ", ".join(sorted(required - set(raw.columns))))
    for field in FIELDS:
        for slot in (1, 2):
            if f"f{slot}_{field}" not in raw.columns:
                raise ValueError(f"Missing column: f{slot}_{field}")

    frame = raw.copy()
    dates = pd.to_datetime(frame["event_date"], errors="coerce")
    outcomes = list(zip(frame["result_f1"].astype(str).str.strip().str.upper(),
                        frame["result_f2"].astype(str).str.strip().str.upper()))
    eligible = dates.notna() & pd.Series(
        [pair in {("W", "L"), ("L", "W")} for pair in outcomes],
        index=frame.index,
    )
    frame = frame.loc[eligible].copy()
    frame["_year"] = dates.loc[eligible].dt.year

    def count(group):
        result = {"fights": int(len(group))}
        for field in FIELDS:
            first = group[f"f1_{field}"].map(lambda x: valid_measure(x, field) is not None)
            second = group[f"f2_{field}"].map(lambda x: valid_measure(x, field) is not None)
            both = int((first & second).sum())
            one = int((first ^ second).sum())
            neither = int((~first & ~second).sum())
            result[field] = {
                "both_valid": both, "one_valid": one, "neither_valid": neither,
                "both_valid_pct": round(100 * both / len(group), 2) if len(group) else None,
            }
        return result

    return {
        "scope": "Completed bouts with valid event dates, historical source as supplied",
        "overall": count(frame),
        "by_year": {str(year): count(group) for year, group in frame.groupby("_year", sort=True)},
        "limitations": [
            "Recorded field coverage is not proof of historical point-in-time availability.",
            "Invalid measurements are counted as unavailable; audit does not impute values.",
            "Outcomes are used only to select completed bouts, never to predict a winner.",
            "Previously studied historical data cannot validate a newly tuned model independently.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fights", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--out", default="results/physical_data_coverage.json")
    args = parser.parse_args()
    report = audit(pd.read_csv(args.fights, low_memory=False))
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

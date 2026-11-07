"""Audit fighter-name/ID collisions in historical data before using them for forecasts.

Usage: python identity_audit.py --history data/ufc_all_fights_wide.csv
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from engine import fighter_key
from predict import normalize


def audit_identities(history, cutoff=None):
    required = {"event_date", "f1_name", "f2_name"}
    missing = required - set(history.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    data = history.copy()
    data["event_date"] = pd.to_datetime(data["event_date"], errors="coerce")
    invalid_dates = int(data["event_date"].isna().sum())
    data = data.dropna(subset=["event_date"])
    if cutoff is not None:
        data = data[data["event_date"] < pd.Timestamp(cutoff)]
    candidates = {}
    for _, row in data.iterrows():
        for slot in (1, 2):
            name = normalize(row.get(f"f{slot}_name", ""))
            if name and name != "nan":
                candidates.setdefault(name, set()).add(fighter_key(row, slot))
    collisions = {name: sorted(ids) for name, ids in sorted(candidates.items())
                  if len(ids) > 1}
    return {"historical_bouts": int(len(data)),
            "invalid_date_rows_excluded": invalid_dates,
            "unique_normalized_names": len(candidates),
            "ambiguous_names": len(collisions),
            "ambiguous_name_ids": collisions}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--before", help="Exclusive forecast cutoff date (YYYY-MM-DD)")
    parser.add_argument("--out", default="results/fighter_identity_audit.json")
    args = parser.parse_args()
    report = audit_identities(pd.read_csv(args.history, low_memory=False), args.before)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Research-only chronological test of age/reach/height missingness correction.

Never replaces production model automatically; train/test/calibration are
split by year exactly as in walk_forward.py. Report each year, including bad
years. This research dataset has been used for earlier experiments.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from engine import FEATURES, prepared_rows, train_model, metrics
from data_quality import SAFE_FEATURES
from calibration import fit_temperature, apply_temperature

OLD_PHYSICAL = ["age_diff", "reach_diff", "height_diff"]
NEW_FEATURES = [f for f in FEATURES if f not in OLD_PHYSICAL] + list(SAFE_FEATURES)


def compare(raw, first=2018, last=2026):
    frame, _ = prepared_rows(raw)
    output = []
    for year in range(first, last + 1):
        tr = frame[frame.event_date.dt.year < year - 1]
        va = frame[frame.event_date.dt.year == year - 1]
        te = frame[frame.event_date.dt.year == year]
        if min(len(tr), len(va), len(te)) < 30 or len(tr) < 100:
            output.append({"year": year, "eligible": False})
            continue
        row = {"year": year, "n": len(te), "eligible": True}
        for label, features in (("baseline", FEATURES), ("pairwise_missingness", NEW_FEATURES)):
            model = train_model(tr, features)
            validation_p = model.predict_proba(va[features].to_numpy(float))[:, 1]
            temperature = fit_temperature(validation_p, va.y.to_numpy(int))
            test_p = apply_temperature(model.predict_proba(te[features].to_numpy(float))[:, 1], temperature)
            row[label] = metrics(te.y.to_numpy(int), test_p)
            row[label]["temperature"] = temperature
        output.append(row)
    return {
        "method": "Matched year-by-year expanding-train and prior-year calibration",
        "years": output,
        "caveat": "Exploratory comparison on previously reused historical data. Do not adopt automatically or claim a betting edge.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fights", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--out", default="results/missingness_comparison.json")
    a = parser.parse_args()
    report = compare(pd.read_csv(a.fights, low_memory=False))
    p = Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

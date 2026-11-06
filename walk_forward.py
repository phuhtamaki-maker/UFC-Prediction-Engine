"""Repeated chronological UFC evaluation.

Each evaluation year is predicted using:
  training: fights BEFORE the previous calendar year
  calibration: the PREVIOUS calendar year only
  test: the stated calendar year only

All feature snapshots are constructed sequentially by engine.prepared_rows.
This reports every eligible year rather than selecting the strongest one.
No positive betting returns are presumed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from calibration import apply_temperature, fit_temperature
from engine import (FEATURES, prepared_rows, train_model, metrics,
                    market_open_probabilities, roi_report)
from selective_evaluation import confidence_report


def year_by_year(raw, start_year=2018, end_year=2026):
    frame, _ = prepared_rows(raw)
    if frame.empty:
        raise ValueError("No completed bouts in input")
    rows = []
    for year in range(int(start_year), int(end_year) + 1):
        train = frame[frame.event_date.dt.year < year - 1]
        calibration = frame[frame.event_date.dt.year == year - 1]
        test = frame[frame.event_date.dt.year == year]
        if len(train) < 100 or len(calibration) < 30 or len(test) < 30:
            rows.append(dict(year=year, eligible=False, training_n=len(train),
                             calibration_n=len(calibration), test_n=len(test),
                             reason="Insufficient training, calibration or evaluation bouts"))
            continue
        model = train_model(train)
        p_val = model.predict_proba(calibration[FEATURES].to_numpy(float))[:, 1]
        temp = fit_temperature(p_val, calibration.y.to_numpy(int))
        p_test = apply_temperature(model.predict_proba(test[FEATURES].to_numpy(float))[:, 1], temp)
        outcomes = test.y.to_numpy(int)
        odds = market_open_probabilities(test)
        paired = np.isfinite(odds)
        market = {}
        if paired.any():
            market = dict(n=int(paired.sum()),
                          model=metrics(outcomes[paired], p_test[paired]),
                          market=metrics(outcomes[paired], odds[paired]))
        confident = confidence_report(outcomes, p_test, odds,
                                      thresholds=(0.6, 0.7, 0.8))
        rows.append(dict(year=year, eligible=True, training_n=len(train),
                         calibration_n=len(calibration), test_n=len(test),
                         temperature=temp,
                         model=metrics(outcomes, p_test),
                         market_same_bouts=market,
                         confidence=confident["thresholds"],
                         roi_illustrative=roi_report(test, p_test)))
    eligible = [row for row in rows if row["eligible"]]
    return {
        "method": "Expanding training ending before previous-year calibration; no same-year outcome labels used",
        "years": rows,
        "evaluated_years": len(eligible),
        "caveats": [
            "Yearly overlapping training sets are NOT independent experiments.",
            "Earlier public data can contain corrections and pre-fight availability cannot always be verified.",
            "This does not establish a betting edge. Historical opening odds may not be executable.",
            "Do not choose the best year or best confidence threshold post hoc.",
            "80% target must include selected number of fights, coverage and uncertainty.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fights", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--out", default="results/walk_forward.json")
    parser.add_argument("--start-year", type=int, default=2018)
    parser.add_argument("--end-year", type=int, default=2026)
    args = parser.parse_args()
    df = pd.read_csv(args.fights, low_memory=False)
    result = year_by_year(df, args.start_year, args.end_year)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

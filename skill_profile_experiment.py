"""Research-only nine-year, matched UFC skill-profile ablation.

The production prediction path stays on the existing ten-feature baseline.
Evaluate the augmented skill model on the exact same years and fights.
All statistics derive from earlier bouts; update only at date boundaries.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from calibration import fit_temperature, apply_temperature
from engine import (FEATURES, SKILL_FEATURES, prepared_rows, train_model,
                    metrics, roi_report, market_open_probabilities)
from selective_evaluation import confidence_report


def evaluate(raw, start_year=2018, end_year=2026):
    frame, _ = prepared_rows(raw)
    yearly = []
    for year in range(start_year, end_year + 1):
        train = frame[frame.event_date.dt.year < year - 1]
        valid = frame[frame.event_date.dt.year == year - 1]
        test = frame[frame.event_date.dt.year == year]
        if min(len(train), len(valid), len(test)) < 30 or len(train) < 100:
            yearly.append(dict(year=year, eligible=False))
            continue
        row = {"year": year, "eligible": True, "test_n": len(test), "models": {}}
        market = market_open_probabilities(test)
        market_ok = np.isfinite(market)
        for label, cols in (("baseline", FEATURES), ("skill_augmented", FEATURES + SKILL_FEATURES)):
            model = train_model(train, cols)
            p_val = model.predict_proba(valid[cols].to_numpy(float))[:, 1]
            temp = fit_temperature(p_val, valid.y.to_numpy(int))
            p_test = apply_temperature(model.predict_proba(test[cols].to_numpy(float))[:, 1], temp)
            top = confidence_report(test.y.to_numpy(int), p_test,
                                    thresholds=(.7,))["thresholds"][0]
            row["models"][label] = {
                "temperature": temp,
                "all": metrics(test.y.to_numpy(int), p_test),
                "top_70": top,
                "paired_to_market": metrics(test.y.to_numpy(int)[market_ok], p_test[market_ok])
                                    if market_ok.any() else None,
                "illustrative_roi": roi_report(test, p_test),
            }
        row["market_paired"] = metrics(test.y.to_numpy(int)[market_ok], market[market_ok]) if market_ok.any() else None
        yearly.append(row)
    return {"method": "Expanding historical training, prior-year validation-only calibration, same-year holdout for both models",
            "years": yearly,
            "notes": ["The baseline is the existing 10 feature model; SKILL_FEATURES are research only.",
                      "No bets are recommended; retrospective data and odds may not be executable.",
                      "Treat this 2018–2026 comparison as exploratory, not an independent future trial."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fights", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--out", default="results/skill_profile_experiment.json")
    args = parser.parse_args()
    frame = pd.read_csv(args.fights, low_memory=False)
    output = evaluate(frame)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

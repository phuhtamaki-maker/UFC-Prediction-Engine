"""Predictions for a user-verified upcoming card using ONLY bouts before the card date.

CSV for upcoming bouts: event_date,f1_name,f2_name plus optional f1_age,
f2_age,f1_reach_cm,f2_reach_cm,f1_height_cm,f2_height_cm.
Provisional probabilities with optional historical validation calibration.\nNo demonstrated betting edge.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from engine import FEATURES, prepared_rows, fighter_key, empty_state, snap, num, train_model
from calibration import apply_temperature, fit_temperature


def normalize(name):
    return " ".join(str(name).strip().casefold().split())


def run_predictions(history, upcoming):
    required = {"event_date", "f1_name", "f2_name"}
    if not required <= set(upcoming.columns):
        raise ValueError("Upcoming card must contain event_date,f1_name,f2_name")
    future = upcoming.copy()
    future["event_date"] = pd.to_datetime(future.event_date, errors="coerce")
    if future.event_date.isna().any():
        raise ValueError("All upcoming fights must have valid dates")
    first_day = future.event_date.min()
    past = history.copy()
    past["event_date"] = pd.to_datetime(past.event_date, errors="coerce")
    past = past[past.event_date < first_day]
    if past.empty:
        raise ValueError("No historical bouts before upcoming card")
    samples, states = prepared_rows(past)
    cutoff = first_day - pd.Timedelta(days=365)
    training = samples[samples.event_date < cutoff]
    validation = samples[samples.event_date >= cutoff]
    # Keep calibration wholly separate from model training; when history is
    # limited, fall back to an explicitly uncalibrated baseline.
    calibrated = len(training) >= 20 and len(validation) >= 30 and training.y.nunique() == 2
    if calibrated:
        model = train_model(training)
        val_p = model.predict_proba(validation[FEATURES].to_numpy(float))[:, 1]
        temp = fit_temperature(val_p, validation.y.to_numpy(int))
    else:
        model = train_model(samples)
        temp = 1.0
    # Link schedule names to historical fighter IDs (which are not supplied on future cards).
    ids_by_name = {}
    for _, r in past.sort_values("event_date").iterrows():
        for index in (1, 2):
            name = normalize(r.get(f"f{index}_name", ""))
            if name and name != "nan":
                ids_by_name[name] = fighter_key(r, index)
    results = []
    for _, row in future.iterrows():
        day = row.event_date.date()
        name_a = str(row.f1_name).strip()
        name_b = str(row.f2_name).strip()
        if not name_a or not name_b or normalize(name_a) == normalize(name_b):
            raise ValueError("Upcoming bout must have two different names")
        keys = (ids_by_name.get(normalize(name_a), normalize(name_a)),
                ids_by_name.get(normalize(name_b), normalize(name_b)))
        s1 = snap(states[keys[0]] if keys[0] in states else empty_state(), day)
        s2 = snap(states[keys[1]] if keys[1] in states else empty_state(), day)
        diff = {
            "elo_diff": (s1["elo"] - s2["elo"]) / 400,
            "win_rate_diff": s1["win_rate"] - s2["win_rate"],
            "ufc_fights_diff": s1["bouts"] - s2["bouts"],
            "ko_losses_diff": s1["ko_losses"] - s2["ko_losses"],
            "recent_ko_diff": s1["recent_ko"] - s2["recent_ko"],
            "days_since_ko_diff": (s1["days_since_ko"] - s2["days_since_ko"]) / 365,
            "rest_days_diff": (s1["rest_days"] - s2["rest_days"]) / 365,
            "recent_form_diff": s1["recent_form"] - s2["recent_form"],
            "opponent_quality_diff": s1["opponent_quality"] - s2["opponent_quality"]}
        for feature, source in (("age_diff", "age"), ("reach_diff", "reach_cm"),
                                ("height_diff", "height_cm")):
            a, b = num(row.get("f1_" + source)), num(row.get("f2_" + source))
            diff[feature] = a - b if a is not None and b is not None else 0.0
        raw_probability = float(model.predict_proba(np.array([[diff[k] for k in FEATURES]]))[0, 1])
        probability = float(apply_temperature([raw_probability], temp)[0])
        results.append({"date": str(day), "fighter_1": name_a, "fighter_2": name_b,
                        "p_fighter_1": round(probability, 4),
                        "p_fighter_2": round(1 - probability, 4),
                        "fighter_1_prior_ufc_bouts": s1["bouts"],
                        "fighter_2_prior_ufc_bouts": s2["bouts"],
                        "historical_temperature": round(temp, 3),
                        "calibration_status": "validation-year calibrated" if calibrated else "NOT calibrated (insufficient history)",
                        "warning": "Limited UFC history" if min(s1["bouts"], s2["bouts"]) < 3
                        else "Experimental probability; independent calibration pending"})
    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--card", required=True)
    parser.add_argument("--out", default="results/upcoming_predictions.csv")
    args = parser.parse_args()
    hist = pd.read_csv(args.history, low_memory=False)
    card = pd.read_csv(args.card)
    result = run_predictions(hist, card)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    print(result.to_string(index=False))
    print("Experimental predictions only; no proven profitability.")


if __name__ == "__main__":
    main()

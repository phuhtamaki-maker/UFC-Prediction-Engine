"""Fail-closed provenance gate for chronological, pre-fight odds evaluation.

Only validated rows may enter value_evaluation.evaluate_value_bets.
This checks timestamp ordering, not the truthfulness of supplied timestamps.
"""
import pandas as pd


REQUIRED = (
    "bout_id", "event_time", "prediction_time", "odds_time",
    "model_commit", "bookmaker", "fighter1_id", "fighter2_id",
    "fighter1_probability", "fighter1_decimal_odds",
    "fighter2_decimal_odds", "fighter1_won",
)


def validate_odds_history(frame):
    missing = sorted(set(REQUIRED) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing provenance columns: {missing}")
    data = frame.copy()
    if data["bout_id"].isna().any() or data["bout_id"].astype(str).str.strip().eq("").any():
        raise ValueError("Missing bout identity")
    if data["bout_id"].duplicated().any():
        raise ValueError("Duplicate bout identity")
    for field in ("model_commit", "bookmaker", "fighter1_id", "fighter2_id"):
        if data[field].isna().any() or data[field].astype(str).str.strip().eq("").any():
            raise ValueError(f"Missing {field}")
    if (data["fighter1_id"].astype(str) == data["fighter2_id"].astype(str)).any():
        raise ValueError("Fighter IDs must differ")
    for field in ("event_time", "prediction_time", "odds_time"):
        data[field] = pd.to_datetime(data[field], utc=True, errors="coerce")
        if data[field].isna().any():
            raise ValueError(f"Missing or invalid {field}")
    if ((data["prediction_time"] >= data["event_time"]) |
            (data["odds_time"] >= data["event_time"])).any():
        raise ValueError("Prediction and odds must predate event")
    if not data["fighter1_won"].isin([0, 1]).all():
        raise ValueError("Only settled binary outcomes supported")
    # Prevent accidental non-numeric input or silently accepting missing prices.
    for field in ("fighter1_probability", "fighter1_decimal_odds", "fighter2_decimal_odds"):
        data[field] = pd.to_numeric(data[field], errors="coerce")
    import numpy as np
    p = data["fighter1_probability"].to_numpy(dtype=float)
    o1 = data["fighter1_decimal_odds"].to_numpy(dtype=float)
    o2 = data["fighter2_decimal_odds"].to_numpy(dtype=float)
    if not (np.isfinite(p).all() and ((p > 0) & (p < 1)).all()):
        raise ValueError("Invalid prediction probabilities")
    if not (np.isfinite(o1).all() and np.isfinite(o2).all()
            and (o1 > 1).all() and (o2 > 1).all()):
        raise ValueError("Missing or invalid bookmaker prices")
    return data

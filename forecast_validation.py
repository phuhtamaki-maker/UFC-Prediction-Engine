"""Validate forecast CSV rows before archiving or scoring.

This validates structure and arithmetic, not provenance or predictive accuracy.
"""
import math
import re
import pandas as pd

REQUIRED = ("date", "fighter_1", "fighter_2", "p_fighter_1", "p_fighter_2")


def _name(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().casefold().split())


def validate_forecast_rows(frame):
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("Forecast must be a DataFrame")
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing forecast columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Empty forecast")
    seen = set()
    for _, row in frame.iterrows():
        raw_date = row["date"]
        if not isinstance(raw_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            raise ValueError("Invalid forecast date: expected YYYY-MM-DD")
        date = pd.to_datetime(raw_date, format="%Y-%m-%d", errors="coerce")
        if pd.isna(date):
            raise ValueError("Invalid forecast date")
        a, b = _name(row["fighter_1"]), _name(row["fighter_2"])
        if not a or not b or a == b or a in ("nan", "none") or b in ("nan", "none"):
            raise ValueError("Invalid fighter names")
        identity = (date.date().isoformat(), tuple(sorted((a, b))))
        if identity in seen:
            raise ValueError("Duplicate forecast bout")
        seen.add(identity)
        try:
            p, q = float(row["p_fighter_1"]), float(row["p_fighter_2"])
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid forecast probability") from exc
        if not (math.isfinite(p) and math.isfinite(q) and 0 <= p <= 1 and 0 <= q <= 1):
            raise ValueError("Invalid forecast probability")
        # predict.py exports four-decimal probabilities; allow independent rounding.
        if abs(p + q - 1) > 0.0002:
            raise ValueError("Forecast probabilities do not sum to one")
    return True

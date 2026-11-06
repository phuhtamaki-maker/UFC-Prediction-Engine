"""Pairwise missingness-safe anthropometric UFC features.

Historic baseline uses legacy 0-imputation; keep it unchanged for fair
prospective comparison. The experimental columns set a missing pair to a
neutral difference of zero, rather than treating a missing age/height/reach
as a literal 0-year-old or 0-cm fighter.
"""
import math

FIELDS = ("age", "reach_cm", "height_cm")
SAFE_FEATURES = ("age_pairwise_diff", "reach_pairwise_diff", "height_pairwise_diff")

def valid_measure(value, field):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    lo, hi = {"age": (16., 65.), "reach_cm": (120., 250.),
              "height_cm": (120., 240.)}[field]
    return x if math.isfinite(x) and lo <= x <= hi else None

def safe_pairwise(row, field):
    a = valid_measure(row.get("f1_" + field), field)
    b = valid_measure(row.get("f2_" + field), field)
    return (a - b if a is not None and b is not None else 0.0,
            int(a is not None and b is not None))

def row_features(row):
    result = {}
    for field, label in zip(FIELDS, SAFE_FEATURES):
        difference, both_available = safe_pairwise(row, field)
        result[label] = difference
        result[label + "_available"] = both_available
    return result

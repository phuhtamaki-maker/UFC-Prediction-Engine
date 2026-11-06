"""Evaluate confidence-filtered UFC picks without hiding coverage or uncertainty.

Thresholds below are predefined descriptive diagnostics, not a strategy
selected for profitability. All outputs are from out-of-sample bouts.
"""
import math
import numpy as np


def wilson_interval(correct, total, z=1.96):
    """Approximate 95% binomial interval. None when no bouts qualify."""
    if total <= 0:
        return [None, None]
    p = correct / total
    denom = 1 + z * z / total
    midpoint = (p + z * z / (2 * total)) / denom
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return [round(max(0, midpoint - radius), 4),
            round(min(1, midpoint + radius), 4)]


def confidence_report(actual, model_prob, market_prob=None, thresholds=(0.6, 0.7, 0.8)):
    y = np.asarray(actual, dtype=int)
    p = np.asarray(model_prob, dtype=float)
    if len(y) != len(p) or not np.isin(y, [0, 1]).all():
        raise ValueError("Mismatched binary outcomes and probabilities")
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError("Probabilities must be finite and in [0,1]")
    market = None if market_prob is None else np.asarray(market_prob, dtype=float)
    if market is not None and len(market) != len(y):
        raise ValueError("Market probability length mismatch")
    output = []
    for minimum in thresholds:
        if not 0.5 <= minimum <= 1:
            raise ValueError("Thresholds must be between 0.5 and 1")
        selected = np.maximum(p, 1 - p) >= minimum
        n = int(selected.sum())
        wins = int(((p >= 0.5) == y)[selected].sum())
        row = {
            "minimum_model_favorite_probability": float(minimum),
            "selected_bouts": n,
            "total_bouts": len(y),
            "coverage": round(n / len(y), 4) if len(y) else 0,
            "correct_predictions": wins,
            "accuracy": round(wins / n, 4) if n else None,
            "accuracy_95pct_wilson_interval": wilson_interval(wins, n),
            "mean_claimed_confidence": round(float(np.maximum(p, 1 - p)[selected].mean()), 4) if n else None,
        }
        if market is not None:
            paired = selected & np.isfinite(market) & (market >= 0) & (market <= 1)
            m = int(paired.sum())
            if m:
                model_wins = int(((p >= 0.5) == y)[paired].sum())
                market_wins = int(((market >= 0.5) == y)[paired].sum())
                row["same_bouts_market_comparison"] = {
                    "n": m,
                    "model_accuracy": round(model_wins / m, 4),
                    "market_accuracy": round(market_wins / m, 4),
                    "market_favorite_agreement": round(float(((p >= .5) == (market >= .5))[paired].mean()), 4),
                }
            else:
                row["same_bouts_market_comparison"] = {"n": 0}
        output.append(row)
    return {
        "note": "Descriptive confidence strata, not a demonstrated betting edge. No threshold chosen post hoc.",
        "thresholds": output
    }

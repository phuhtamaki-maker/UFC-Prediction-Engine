"""Predeclared, out-of-sample single-bet value diagnostics; never a betting guarantee.

Inputs must be timestamp-aligned: probabilities frozen before quoted decimal odds
and before the fight. This module does not select thresholds using outcomes.
"""
import numpy as np


def evaluate_value_bets(outcomes, fighter1_probabilities, fighter1_decimal_odds,
                        fighter2_decimal_odds, min_edge=0.05):
    """Flat 1-unit stakes; no bets when either side lacks a verified price."""
    y = np.asarray(outcomes)
    p = np.asarray(fighter1_probabilities, dtype=float)
    o1 = np.asarray(fighter1_decimal_odds, dtype=float)
    o2 = np.asarray(fighter2_decimal_odds, dtype=float)
    if not (y.ndim == p.ndim == o1.ndim == o2.ndim == 1 and
            len(y) == len(p) == len(o1) == len(o2)):
        raise ValueError("Inputs must be equal-length 1-D arrays")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("Outcomes must be binary (1=fighter 1 wins)")
    if not np.isfinite(p).all() or ((p <= 0) | (p >= 1)).any():
        raise ValueError("Model probabilities must be strictly between zero and one")
    if not np.isfinite(min_edge) or not 0 <= min_edge < 1:
        raise ValueError("Invalid edge threshold")
    valid = np.isfinite(o1) & np.isfinite(o2) & (o1 > 1) & (o2 > 1)
    edge1 = p * o1 - 1
    edge2 = (1 - p) * o2 - 1
    choose1 = valid & (edge1 >= min_edge) & (edge1 > edge2)
    choose2 = valid & (edge2 >= min_edge) & (edge2 > edge1)
    selected = choose1 | choose2
    profits = np.where(choose1, np.where(y == 1, o1 - 1, -1),
                       np.where(choose2, np.where(y == 0, o2 - 1, -1), 0))
    n = int(selected.sum())
    return {
        "total_bouts": len(y),
        "priced_bouts": int(valid.sum()),
        "bets": n,
        "no_bet_bouts": int(len(y) - n),
        "min_expected_roi_edge": float(min_edge),
        "flat_stake_units": n,
        "profit_units": round(float(profits.sum()), 4),
        "realized_roi": round(float(profits.sum() / n), 4) if n else None,
        "note": "Research only. Requires frozen pre-fight predictions and contemporaneous odds; no profitability demonstrated."
    }

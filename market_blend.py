"""Validate an opening-odds/independent-model probability blend chronologically.

Market probabilities are only available *after* the historical opening line is
recorded. Do not use this blend as a prediction before those odds existed.
The coefficient is chosen using validation bouts only; report holdout results
regardless of outcome. No claim of profitable betting is implied.
"""
import numpy as np
from sklearn.metrics import log_loss


def mix_probabilities(model, market, model_weight):
    """Symmetric under fighter reversal. Missing odds -> model-only fallback."""
    m = np.asarray(model, dtype=float)
    q = np.asarray(market, dtype=float)
    if m.shape != q.shape or not 0 <= model_weight <= 1:
        raise ValueError("Bad probability shapes or weight")
    if not np.isfinite(m).all() or ((m <= 0) | (m >= 1)).any():
        raise ValueError("Model probabilities must lie in (0,1)")
    mask = np.isfinite(q) & (q > 0) & (q < 1)
    blended = m.copy()
    blended[mask] = model_weight * m[mask] + (1 - model_weight) * q[mask]
    return blended


def fit_model_weight(validation_targets, model_probability, market_probability):
    """Select coefficient on validation fights with BOTH opening odds.

    Predeclared five-point search includes market-only and model-only. Missing
    odds cannot be used to optimize the coefficient. Ties prefer market-only.
    """
    y = np.asarray(validation_targets, dtype=int)
    model = np.asarray(model_probability, dtype=float)
    market = np.asarray(market_probability, dtype=float)
    if len(y) != len(model) or len(y) != len(market):
        raise ValueError("Lengths differ")
    good = np.isfinite(market) & (market > 0) & (market < 1)
    if good.sum() < 30:
        return {"model_weight": 0.0, "validation_n": int(good.sum()),
                "note": "Insufficient paired validation odds: using market only where available."}
    weights = [0.0, 0.25, 0.5, 0.75, 1.0]
    results = [float(log_loss(y[good], mix_probabilities(model[good], market[good], w), labels=[0, 1]))
               for w in weights]
    best = int(np.argmin(results))
    return {"model_weight": weights[best], "validation_n": int(good.sum()),
            "validation_log_loss": round(results[best], 5),
            "market_only_validation_log_loss": round(results[0], 5),
            "note": "Validation-only coefficient; model training is pre-validation."}

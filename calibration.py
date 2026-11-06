"""Conservative, symmetric probability calibration.

Fit temperature only to a separate historical validation set, never the test set.
This is research code and is not a guarantee of calibrated real-world outcomes.
"""
import numpy as np
from sklearn.metrics import log_loss


def apply_temperature(probabilities, temperature):
    """p(1-p) symmetry is preserved when fighter order is reversed."""
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-8, 1 - 1e-8)
    logits = np.log(p) - np.log1p(-p)
    z = np.clip(logits / float(temperature), -100, 100)
    return 1 / (1 + np.exp(-z))


def fit_temperature(validation_probability, observed):
    """Choose one global temperature by validation-only log loss.

    A coarse fixed, predeclared grid avoids optimizers choosing extreme
    parameters from small validation sets. Baseline T=1 always included.
    """
    y = np.asarray(observed, dtype=int)
    p = np.asarray(validation_probability, dtype=float)
    if len(y) < 30 or len(y) != len(p) or not np.isin(y, [0, 1]).all():
        raise ValueError("Need >=30 binary validation observations")
    if not np.isfinite(p).all() or (p <= 0).any() or (p >= 1).any():
        raise ValueError("Validation probabilities must lie strictly between 0 and 1")
    candidates = np.array([0.5, 0.625, 0.8, 1.0, 1.25, 1.6, 2.0, 2.5, 3.2, 4.0])
    losses = [
        float(log_loss(y, apply_temperature(p, t), labels=[0, 1]))
        for t in candidates
    ]
    return float(candidates[int(np.argmin(losses))])

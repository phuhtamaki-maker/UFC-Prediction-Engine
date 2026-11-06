# Missing fighter data experiment — 7 November 2026

## Why this matters
The current baseline treats a missing fighter age, height or reach as **zero** before subtracting the opponent's measurement. That can introduce unrealistic physical gaps (e.g. an apparently 0-year-old fighter) and misleading model confidence.

## Research implementation
- `data_quality.py`: research-only safe pairwise differences, neutral when either measurement is absent or implausible.
- `engine.py`: produces those additional research columns, without adding them to the **active ten-feature model**.
- `missingness_experiment.py`: replaces the three legacy age/reach/height differences with neutral pairwise differences only in the experimental model.
- `tests/test_data_quality.py`: checks missing, invalid, reversed and fully observed cases.
- GitHub test and historical run succeeded: https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42301880648 .

## Matched 2018–2026 walk-forward results
Train on older data, calibrate on the previous year only, score the current year. Same 4,387 fights for both models.

| Metric | Existing baseline | Pairwise missingness experiment |
|---|---:|---:|
| Correct picks | **2622 / 4387 = 59.77%** | 2586 / 4387 = 58.95% |
| Weighted Brier score (lower better) | **0.23692** | 0.23802 |
| Weighted log loss (lower better) | **0.66629** | 0.66860 |

The experimental change is conceptually safer but **did not improve this historical accuracy or probability scoring**. Keep the baseline active.

## Follow-on priorities
1. Measure frequency of pairwise missingness and identify where the source tends to omit values.
2. Study explicitly flagged missingness indicators (rather than just neutral substitution), using only pre-fight available values.
3. Verify production forecast inputs and fighter IDs against the historic data to avoid unknown-fighter and missingness bias.
4. Use future, sealed and genuinely new fights to judge any adoption decision. The 2018–2026 dataset has already been reused in multiple experiments and is not independent confirmation of improvements.

No claimed 80% accuracy or betting advantage. This result illustrates the importance of recording unsuccessful experiments.

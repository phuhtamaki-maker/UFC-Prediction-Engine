# Opponent strength and recent form experiment — 6 Nov 2026

## Goal
Test whether tracking each fighter's last five UFC results and the pre-fight Elo strength of opponents improves the UFC Prediction Engine. Prior results alone can be misleading without considering opponent quality.

## Implementation
- `engine.py` now computes two strictly historical research fields:
  - `recent_form_diff`: Laplace-smoothed win rate in the **five prior UFC fights**.
  - `opponent_quality_diff`: average **pre-fight** Elo of prior five UFC opponents, relative to 1500.
- Both are constructed from results available before the target fight date; fights on the same date do not update one another's histories.
- `predict.py` can reconstruct the same research fields for a future fight.
- Dedicated tests ensure no future outcomes or same-day results leak into these fields.

## Chronological 2018–2026 backtest

Nine separate evaluation years using only earlier years for training and the immediately previous year for calibration. 4,387 fights total.

| Metric | Existing ten-feature baseline | Experimental twelve-feature model |
| --- | ---: | ---: |
| All fights correct | 2622/4387 = **59.77%** | 2595/4387 = **59.15%** |
| Picks with >=70% estimated confidence | 337/446 = **75.56%** | 363/491 = **73.93%** |
| Number of simulated wagers | 3318 | 3299 |
| Simulated unit profit | −169.604 | −192.782 |
| Simulated ROI | **−5.11%** | **−5.84%** |

The experimental features did **not** improve these metrics. This is a *negative result*, not a successful accuracy improvement. The reference test was https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42293465247 .

## Decision
**Retain the baseline 10 features as the active training and forecast set.** The two historical research fields remain computed as `EXPERIMENTAL_FEATURES`, but are not used by default. No post-hoc tuning of the 2018–2026 data to force an 80% result.

## Limitations and next checks
- Pre-fight opponent Elo is a simplified approximation of opponent quality, not an external ranking.
- Last-five samples are small, with differences in weight classes and eras.
- This comparison used repeated prior periods, but the choice to disable experimental features is informed by observed results; future independent data is needed for final confirmation.
- Data recorded after the fact may include retrospective corrections.
- Historical opening odds may not have been bettable; simulated ROI is not proven expected returns.

## Next development
Improve fighter identity matching and investigate genuinely pre-fight-sourced ranking, weight class and opponent-strength measures on validation history; preserve the initial 10-feature benchmark.

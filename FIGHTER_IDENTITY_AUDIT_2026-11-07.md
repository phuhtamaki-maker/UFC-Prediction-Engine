# Historical fighter identity audit — 2026-11-07

## Verified execution
- Workflow: [Fighter identity audit run #42389859152](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42389859152)
- Result: success, using `nlbair/ufc-data` downloaded in GitHub Actions.
- Exclusive historical cutoff: 2026-11-07.
- Historical rows included: **6,743**.
- Invalid date rows excluded: **0**.
- Unique normalized fighter names: **2,066**.
- Normalized names mapping to multiple fighter IDs: **1**.

## Identified ambiguity
`bruno silva` maps to **two distinct historical fighter IDs**:
- `12ebd7d157e91701`
- `294aa73dbf37d281`

This is a name-to-ID collision, **not** evidence of a wrong prediction or mistaken historical labeling. The existing `predict.py` logic rejects ambiguous historical names rather than silently choosing one.

## Reproducibility and limits
Run `python identity_audit.py --before 2026-11-07` on the same dataset version to reproduce. The upstream CSV is downloaded from a mutable URL, so results could change as upstream data changes. The run's uploaded `fighter-identity-audit` artifact preserves the JSON report, but does not pin the source CSV hash. Future work should record the dataset SHA-256 and publication snapshot; historical cutoff by bout date is not a substitute for proving point-in-time availability.

No model features, weights, forecast probabilities, or betting claims were changed by this audit.

# Physical attribute coverage audit (research only)

This addition measures how often historical completed UFC fights contain **two valid observations** for age, reach and height. It reports overall and annual both-valid, one-valid and neither-valid counts using the existing `data_quality.valid_measure` bounds.

Run `python physical_data_audit.py --fights data/ufc_all_fights_wide.csv`. The JSON output is written to `results/physical_data_coverage.json`. A GitHub Actions workflow can also generate and attach the JSON.

**Why:** the current baseline's zero-imputation may create artificial physical differences, but simply replacing it with neutral pairwise gaps *reduced* historical performance (see `MISSING_DATA_EXPERIMENT.md`). Before trying further improvements, quantify data coverage and its year-to-year shifts.

**Safeguards:** the script only observes missingness and does not change the ten-feature production model, adjust predictions, use future statistics to train, or claim improved accuracy. Even a field present in today's historical export might not have been known before the past fight. The research dataset has already been reused and should not be mistaken for an untouched validation sample.

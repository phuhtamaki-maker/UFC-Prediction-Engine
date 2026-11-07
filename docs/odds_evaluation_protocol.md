# Historical odds comparison: data acceptance checklist

Before publishing a realized ROI or claiming a betting edge, each evaluated bout must have:

1. A unique event and fighter identity mapping (no unresolved duplicate names).
2. An **immutable pre-fight prediction** with creation timestamp, model version/commit, and fighter orientation.
3. A **contemporaneous bookmaker decimal price** for both sides, with bookmaker, captured timestamp, and provenance.
4. Confirmation that the prediction and price were available before the event; no result-derived inputs.
5. A clearly defined settlement rule for draws, no-contests, cancellations, and voids; the current binary evaluator must not be used for these outcomes.
6. Chronological separation between training, parameter selection and untouched holdout.
7. All priced fights counted, including no-bets, to prevent cherry-picking; report bet count, coverage, units, ROI and uncertainty.
8. Any chosen edge threshold must be fixed before inspecting holdout outcomes; account for bookmaker margin and achievable odds.

The research function in `value_evaluation.py` is **not** a data ingestion or provenance validator.
Passing unit tests does not establish that historical odds existed or were obtainable at a particular timestamp.
No verified historical ROI is available from this branch yet. Do not use these outputs to justify real-money stakes.

Next implementation: create a timestamped, provenance-checked evaluation dataset and an independent untouched holdout report.

# Frozen pre-event prediction archive protocol (research)

This is a proposed record-keeping protocol, not proof that past predictions were frozen or that historical ROI is verified.

## Before the event
- Save the original prediction CSV **before the first relevant bout starts**; never overwrite it after results are known.
- Record an unambiguous UTC creation time and event cutoff, the exact Git commit SHA, model feature list, training-data cutoff, source dataset SHA-256, input card SHA-256, output CSV SHA-256, and the exact command used.
- Keep fighter names, event date, both predicted probabilities, model warnings and calibration status. Record each bout's stable identifier if available; reject duplicate identifiers.
- Record the archival location and an immutable commit or artifact identifier. A file created after an event cannot retroactively prove a pre-event forecast.
- Distinguish a timestamp written *inside* a file from independent evidence of when it was published. Prefer a timestamped external artifact or commit created before the event.

## After the event
- Store official outcomes separately. Join only by validated bout identity; explicitly account for missing, cancelled, no-contest and ambiguous matches.
- Report **correct / evaluated**, accuracy, **evaluated / scheduled** coverage, and the number of excluded bouts with reasons.
- Report ROI only if original pre-bet odds, actual placed stakes, bet selections, settlement and any refunds are independently documented. ROI = net settled profit / total amount staked. If there are no settled stakes, ROI is undefined.
- Never substitute historical backtest prices for executed bets or call retrospective calculations realized betting profits.
- Keep preliminary conversation-derived picks separate from independently verifiable frozen model forecasts.

## Acceptance checks
1. No outcome or post-event statistic is available to the forecast pipeline.
2. All timestamps have explicit timezones and satisfy the pre-bout cutoff.
3. Original predictions and hashes are unchanged after settlement.
4. Missing or duplicate bout identifiers cause review rather than silent counting.
5. Report includes numerator, denominator, coverage, and a provenance warning.

This document does not change the active 10-feature model, weights, thresholds, or staking rules.

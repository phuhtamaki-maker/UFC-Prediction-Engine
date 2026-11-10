"""Score ONLY archived, hash-verified UFC predictions against completed bouts.

Do not infer an outcome for cancelled, replaced, unfinished or ambiguous fights.
Never regenerate the archived predictions after outcomes become known.
"""
import argparse
import datetime as dt
import hashlib
import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from selective_evaluation import confidence_report, wilson_interval


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for part in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def normalize(value):
    text = unicodedata.normalize("NFKD", str(value).strip().casefold())
    return " ".join("".join(ch for ch in text if not unicodedata.combining(ch)
                            and (ch.isalnum() or ch.isspace())).split())


def strict_event_date(value):
    """Reject ambiguous or noncanonical dates before joining fight records."""
    if (not isinstance(value, str) or len(value) != 10
            or value[4] != "-" or value[7] != "-"
            or not all("0" <= ch <= "9" for ch in value[:4] + value[5:7] + value[8:])):
        raise ValueError("Event date must use YYYY-MM-DD")
    return dt.date.fromisoformat(value).isoformat()


def key(date, one, two):
    day = strict_event_date(date)
    names = (normalize(one), normalize(two))
    if not all(names) or names[0] == names[1]:
        raise ValueError("Invalid or identical fighter names")
    return day, tuple(sorted(names))


def score(frozen_csv, manifest_json, completed_csv):
    manifest = json.loads(Path(manifest_json).read_text(encoding="utf-8"))
    if file_sha256(frozen_csv) != manifest["predictions_sha256"]:
        raise ValueError("Frozen predictions failed SHA-256 verification")
    # An unchanged file is not necessarily a genuine *pre-event* forecast.
    # Enforce chronology using immutable manifest metadata as an additional
    # guard. GitHub Actions run timing should be checked independently.
    generated_text = manifest.get("generated_utc")
    cutoff_text = manifest.get("cutoff_utc")
    if generated_text is not None or cutoff_text is not None:
        if not generated_text or not cutoff_text:
            raise ValueError("Both generated_utc and cutoff_utc are required")
        def moment(value):
            parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("Manifest timestamps require UTC offsets")
            return parsed.astimezone(dt.timezone.utc)
        generated = moment(generated_text)
        cutoff = moment(cutoff_text)
        if generated >= cutoff:
            raise ValueError("Post-cutoff forecast cannot count as pre-event")
    else:
        # Legacy unit fixtures may omit timestamps; such snapshots cannot
        # qualify as independently time-verified forecasts.
        generated = cutoff = None
    frozen = pd.read_csv(frozen_csv, dtype={"date": "str"})
    if len(frozen) != manifest["prediction_count"]:
        raise ValueError("Frozen row count differs from manifest")
    needed = {"date", "fighter_1", "fighter_2", "p_fighter_1", "p_fighter_2"}
    if not needed <= set(frozen.columns):
        raise ValueError("Frozen data lacks required columns")
    if generated is not None:
        event_days = frozen["date"].map(strict_event_date)
        if (event_days < cutoff.date().isoformat()).any():
            raise ValueError("Frozen card contains event before UTC cutoff date")
    completed = pd.read_csv(completed_csv, dtype={"event_date": "str"})
    required = {"event_date", "f1_name", "f2_name", "result_f1", "result_f2"}
    if not required <= set(completed.columns):
        raise ValueError("Results data lacks required columns")
    results = {}
    ambiguous = set()
    for _, fight in completed.iterrows():
        k = key(fight.event_date, fight.f1_name, fight.f2_name)
        if k in results:
            ambiguous.add(k)
        else:
            results[k] = fight
    seen = set()
    details = []
    y, p = [], []
    for _, pred in frozen.iterrows():
        k = key(pred.date, pred.fighter_1, pred.fighter_2)
        if k in seen:
            raise ValueError("Frozen file contains duplicate fight")
        seen.add(k)
        a, b = float(pred.p_fighter_1), float(pred.p_fighter_2)
        if not (np.isfinite(a) and np.isfinite(b)
                and 0 <= a <= 1 and 0 <= b <= 1
                and abs(a + b - 1) <= 0.00011):
            raise ValueError("Invalid frozen probabilities")
        state = "unmatched"
        actual = None
        if k in ambiguous:
            state = "ambiguous_duplicate_result"
        elif k in results:
            r = results[k]
            outcome = (str(r.result_f1).strip().upper(), str(r.result_f2).strip().upper())
            if outcome in (("W", "L"), ("L", "W")):
                actual = 1 if (outcome[0] == "W") == (normalize(r.f1_name) == normalize(pred.fighter_1)) else 0
                p.append(a)
                y.append(actual)
                state = "scored"
            else:
                state = "non_decisive_or_not_complete"
        details.append({"date": str(pred.date), "fighter_1": str(pred.fighter_1),
                        "fighter_2": str(pred.fighter_2), "status": state,
                        "p_fighter_1": a, "actual_fighter_1_win": actual,
                        "winner_pick": ("no_pick" if a == 0.5 else
                                        ("fighter_1" if a > 0.5 else "fighter_2")) if state == "scored" else None})
    total = len(frozen)
    counted = len(y)
    # Exact 50/50 forecasts are probability estimates, not directional picks.
    # Retain them in coverage and proper scoring rules, but not pick accuracy.
    directional = [(prob, outcome) for prob, outcome in zip(p, y) if prob != 0.5]
    picks = len(directional)
    ties = counted - picks
    correct = sum((prob > 0.5) == bool(outcome) for prob, outcome in directional)
    return {
        "manifest_sha256": file_sha256(manifest_json),
        "frozen_predictions_sha256": manifest["predictions_sha256"],
        "github_forecast_run": manifest.get("github_run_id"),
        "snapshot_chronology_checked": generated is not None,
        "generated_utc": generated_text,
        "cutoff_utc": cutoff_text,
        "total_frozen": total,
        "completed_scored": counted,
        "excluded_or_unmatched": total - counted,
        "coverage": round(counted / total, 4) if total else 0,
        "correct": correct,
        "directional_picks": picks,
        "ties": ties,
        "accuracy": round(correct / picks, 4) if picks else None,
        "accuracy_95pct_wilson_interval": wilson_interval(correct, picks),
        "confidence_diagnostics": confidence_report(y, p, thresholds=(0.6, 0.7, 0.8)),
        "brier": round(float(brier_score_loss(y, p)), 4) if counted else None,
        "log_loss": round(float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1])), 4) if counted else None,
        "warning": "Descriptive statistics for scored bouts only; missing results reduce coverage and may bias estimates. Confidence thresholds are predetermined, not betting recommendations. No demonstrated profitability.",
        "fights": details,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--out", default="results/verified_score.json")
    args = parser.parse_args()
    answer = score(args.frozen, args.manifest, args.results)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(answer, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(answer, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

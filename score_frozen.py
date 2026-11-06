"""Score ONLY archived, hash-verified UFC predictions against completed bouts.

Do not infer an outcome for cancelled, replaced, unfinished or ambiguous fights.
Never regenerate the archived predictions after outcomes become known.
"""
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss


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


def key(date, one, two):
    day = pd.to_datetime(date, errors="raise").date().isoformat()
    names = (normalize(one), normalize(two))
    if not all(names) or names[0] == names[1]:
        raise ValueError("Invalid or identical fighter names")
    return day, tuple(sorted(names))


def score(frozen_csv, manifest_json, completed_csv):
    manifest = json.loads(Path(manifest_json).read_text(encoding="utf-8"))
    if file_sha256(frozen_csv) != manifest["predictions_sha256"]:
        raise ValueError("Frozen predictions failed SHA-256 verification")
    frozen = pd.read_csv(frozen_csv, dtype={"date": "str"})
    if len(frozen) != manifest["prediction_count"]:
        raise ValueError("Frozen row count differs from manifest")
    needed = {"date", "fighter_1", "fighter_2", "p_fighter_1", "p_fighter_2"}
    if not needed <= set(frozen.columns):
        raise ValueError("Frozen data lacks required columns")
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
                        "p_fighter_1": a, "actual_fighter_1_win": actual})
    total = len(frozen)
    counted = len(y)
    correct = int(sum((np.array(p) >= 0.5) == np.array(y))) if counted else 0
    return {
        "manifest_sha256": file_sha256(manifest_json),
        "frozen_predictions_sha256": manifest["predictions_sha256"],
        "github_forecast_run": manifest.get("github_run_id"),
        "total_frozen": total,
        "completed_scored": counted,
        "excluded_or_unmatched": total - counted,
        "coverage": round(counted / total, 4) if total else 0,
        "correct": correct,
        "accuracy": round(correct / counted, 4) if counted else None,
        "brier": round(float(brier_score_loss(y, p)), 4) if counted else None,
        "log_loss": round(float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1])), 4) if counted else None,
        "warning": "Only exact matched concluded bouts scored. Missing/cancelled/replaced fights excluded; no claim of betting profitability.",
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

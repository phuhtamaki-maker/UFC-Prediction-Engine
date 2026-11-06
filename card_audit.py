"""Audit a current UFC bout card against original, SHA-verified frozen picks.

A changed matchup is NOT a loss. This is a schedule comparison, not a
confirmation of official cancellations or a post-event results scorer.
Never regenerate or modify the frozen predictions.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import pandas as pd
from score_frozen import file_sha256, key, normalize


def audit_card(frozen_csv, manifest_json, current_card_csv):
    manifest = json.loads(Path(manifest_json).read_text(encoding="utf-8"))
    if file_sha256(frozen_csv) != manifest["predictions_sha256"]:
        raise ValueError("Frozen predictions failed SHA-256 verification")
    frozen = pd.read_csv(frozen_csv)
    current = pd.read_csv(current_card_csv)
    if not {"date", "fighter_1", "fighter_2"} <= set(frozen.columns):
        raise ValueError("Frozen predictions lack date or fighter fields")
    if not {"event_date", "f1_name", "f2_name"} <= set(current.columns):
        raise ValueError("Current card lacks event date or fighter fields")
    if len(frozen) != manifest["prediction_count"]:
        raise ValueError("Frozen prediction count mismatch")
    old_keys = [key(r.date, r.fighter_1, r.fighter_2) for _, r in frozen.iterrows()]
    new_keys = [key(r.event_date, r.f1_name, r.f2_name) for _, r in current.iterrows()]
    if len(set(old_keys)) != len(old_keys) or len(set(new_keys)) != len(new_keys):
        raise ValueError("Duplicate fights in frozen or current card")
    old_set, new_set = set(old_keys), set(new_keys)
    unmatched = [pair for pair in new_keys if pair not in old_set]
    old_missing = [pair for pair in old_keys if pair not in new_set]
    detail = []
    for old in old_keys:
        if old in new_set:
            status = "unchanged"
            candidates = []
        else:
            # A fighter in the old pair can be paired with someone new, but
            # one shared fighter alone does not prove a cancellation/change.
            candidates = [new for new in unmatched
                          if new[0] == old[0] and len(set(new[1]) & set(old[1])) == 1]
            status = "possible_opponent_change" if len(candidates) == 1 else (
                "not_listed" if len(candidates) == 0 else "ambiguous_change")
        detail.append({"date": old[0], "frozen_pair": list(old[1]),
                       "status": status,
                       "possible_current_pairs": [list(item[1]) for item in candidates]})
    counts = Counter(item["status"] for item in detail)
    return {
        "source_prediction_sha256": manifest["predictions_sha256"],
        "frozen_count": len(old_keys),
        "current_card_count": len(new_keys),
        "unchanged": counts["unchanged"],
        "possible_opponent_change": counts["possible_opponent_change"],
        "not_listed": counts["not_listed"],
        "ambiguous_change": counts["ambiguous_change"],
        "newly_listed_pairs": [{"date": day, "pair": list(names)} for day, names in unmatched],
        "warning": "Schedule comparison only; changes require verification with official bout announcements. Frozen predictions are never edited.",
        "frozen_bouts": detail,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--card", required=True)
    parser.add_argument("--out", default="results/card_audit.json")
    args = parser.parse_args()
    report = audit_card(args.frozen, args.manifest, args.card)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

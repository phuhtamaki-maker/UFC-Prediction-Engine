"""Pre-fight UFC prediction research. Data credit: nlbair/ufc-data (CC BY 4.0).
Research prototype; no verified betting edge. Never train on target fight statistics.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DATA_URL = "https://raw.githubusercontent.com/nlbair/ufc-data/main/data/ufc_all_fights_wide.csv"
FEATURES = ["elo_diff", "win_rate_diff", "ufc_fights_diff", "ko_losses_diff",
            "recent_ko_diff", "days_since_ko_diff", "rest_days_diff",
            "age_diff", "reach_diff", "height_diff"]

def num(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None

def american_decimal(value):
    v = num(value)
    if v is None or abs(v) < 100:
        return None
    return 1 + v / 100 if v > 0 else 1 + 100 / abs(v)

def fighter_key(row, slot):
    fid = str(row.get(f"f{slot}_id", "")).strip()
    if fid and fid.lower() != "nan":
        return fid
    return " ".join(str(row.get(f"f{slot}_name", "")).strip().casefold().split())

def empty_state():
    return dict(elo=1500., bouts=0, wins=0, ko_losses=0, last_ko=None, last_bout=None)

def snap(state, day):
    ko_days = (day - state["last_ko"]).days if state["last_ko"] else None
    rest_days = (day - state["last_bout"]).days if state["last_bout"] else None
    return dict(elo=state["elo"], win_rate=(state["wins"] + 1) / (state["bouts"] + 2),
                bouts=state["bouts"], ko_losses=state["ko_losses"],
                recent_ko=int(ko_days is not None and ko_days <= 180),
                days_since_ko=min(ko_days, 1095) if ko_days is not None else 1095,
                rest_days=min(rest_days, 1095) if rest_days is not None else 365)

def prepared_rows(df):
    """All feature snapshots precede the bout. Same-date bouts never leak into each other."""
    needed = {"event_date", "f1_name", "f2_name", "result_f1", "result_f2"}
    if not needed <= set(df.columns):
        raise ValueError(f"Missing columns: {sorted(needed - set(df.columns))}")
    data = df.copy()
    data["event_date"] = pd.to_datetime(data.event_date, errors="coerce")
    data = data.dropna(subset=["event_date"]).sort_values("event_date", kind="stable")
    states = defaultdict(empty_state)
    observations = []
    for timestamp, group in data.groupby("event_date", sort=True):
        day = timestamp.date()
        pending = []
        for _, row in group.iterrows():
            a, b = fighter_key(row, 1), fighter_key(row, 2)
            if not a or not b or a == b:
                continue
            sa, sb = snap(states[a], day), snap(states[b], day)
            values = {
                "elo_diff": (sa["elo"] - sb["elo"]) / 400,
                "win_rate_diff": sa["win_rate"] - sb["win_rate"],
                "ufc_fights_diff": sa["bouts"] - sb["bouts"],
                "ko_losses_diff": sa["ko_losses"] - sb["ko_losses"],
                "recent_ko_diff": sa["recent_ko"] - sb["recent_ko"],
                "days_since_ko_diff": (sa["days_since_ko"] - sb["days_since_ko"]) / 365,
                "rest_days_diff": (sa["rest_days"] - sb["rest_days"]) / 365,
                "age_diff": (num(row.get("f1_age")) or 0) - (num(row.get("f2_age")) or 0),
                "reach_diff": (num(row.get("f1_reach_cm")) or 0) - (num(row.get("f2_reach_cm")) or 0),
                "height_diff": (num(row.get("f1_height_cm")) or 0) - (num(row.get("f2_height_cm")) or 0)}
            outcome = (str(row["result_f1"]).strip().upper(), str(row["result_f2"]).strip().upper())
            if outcome not in (("W", "L"), ("L", "W")):
                continue
            sample = dict(event_date=timestamp, f1_name=row["f1_name"], f2_name=row["f2_name"],
                          f1_open=num(row.get("f1_open")), f2_open=num(row.get("f2_open")),
                          y=int(outcome[0] == "W"), **values)
            # Deterministic listing randomization avoids f1-is-usually-winner label leakage.
            identity = f'{row.get("fight_id", "")}|{a}|{b}|{timestamp}'
            if int(hashlib.sha256(identity.encode()).hexdigest()[:8], 16) % 2:
                for feat in FEATURES:
                    sample[feat] *= -1
                sample["f1_name"], sample["f2_name"] = sample["f2_name"], sample["f1_name"]
                sample["f1_open"], sample["f2_open"] = sample["f2_open"], sample["f1_open"]
                sample["y"] = 1 - sample["y"]
            observations.append(sample)
            pending.append((a, b, int(outcome[0] == "W"), str(row.get("finish_type", "")).casefold().strip()))
        for a, b, winner_a, finish_type in pending:
            sa, sb = states[a], states[b]
            expected = 1 / (1 + 10 ** ((sb["elo"] - sa["elo"]) / 400))
            change = 24 * (winner_a - expected)
            sa["elo"] += change
            sb["elo"] -= change
            for fighter, won in ((sa, winner_a), (sb, 1 - winner_a)):
                fighter["bouts"] += 1
                fighter["wins"] += won
                fighter["last_bout"] = day
            if finish_type == "ko_tko":
                victim = sb if winner_a else sa
                victim["ko_losses"] += 1
                victim["last_ko"] = day
    return pd.DataFrame(observations), states

def metrics(actual, probability):
    return dict(n=len(actual),
                accuracy=round(float(accuracy_score(actual, probability >= .5)), 4),
                brier=round(float(brier_score_loss(actual, probability)), 4),
                log_loss=round(float(log_loss(actual, np.clip(probability, 1e-6, 1 - 1e-6), labels=[0, 1])), 4))

def train_model(train):
    if len(train) < 20 or train.y.nunique() < 2:
        raise ValueError("Need at least 20 completed bouts and both winning outcomes")
    x = train[FEATURES].to_numpy(float)
    y = train.y.to_numpy(int)
    model = make_pipeline(StandardScaler(with_mean=False),
                          LogisticRegression(C=.1, max_iter=2000, fit_intercept=False))
    model.fit(np.vstack((x, -x)), np.concatenate((y, 1 - y)))
    return model

def market_open_probabilities(frame):
    """No-vig opening-line probabilities; None for missing/malformed odds."""
    values = []
    for _, row in frame.iterrows():
        da = american_decimal(row.get("f1_open"))
        db = american_decimal(row.get("f2_open"))
        if da is None or db is None:
            values.append(float("nan"))
        else:
            a, b = 1 / da, 1 / db
            values.append(a / (a + b))
    return np.array(values, dtype=float)


def market_comparison(frame, model_probability):
    market = market_open_probabilities(frame)
    available = np.isfinite(market)
    if not available.any():
        return {"n": 0, "note": "No paired opening odds available."}
    outcomes = frame.y.to_numpy(int)[available]
    return {
        "n": int(available.sum()),
        "model_same_bouts": metrics(outcomes, model_probability[available]),
        "market_no_vig": metrics(outcomes, market[available]),
        "note": "Opening-line market baseline on identical fights; availability of quoted prices not verified."
    }


def roi_report(df, probabilities, edge=.05):
    units = 0
    profit = 0.
    for (_, row), p in zip(df.iterrows(), probabilities):
        bets = []
        for outcome, chance, col in ((1, p, "f1_open"), (0, 1 - p, "f2_open")):
            dec = american_decimal(row.get(col))
            if dec is not None and chance * dec - 1 > edge:
                bets.append((chance * dec - 1, outcome, dec))
        if bets:
            _, outcome, dec = max(bets)
            units += 1
            profit += dec - 1 if int(row.y) == outcome else -1
    return dict(bets=units, units_staked=units, profit_units=round(profit, 3),
                roi=round(profit / units, 4) if units else None,
                caveat="Historical opening odds may not be executable; no fees or slippage modeled.")

def run(fights, out_dir="results", train_end="2024-01-01", valid_end="2025-01-01"):
    raw = pd.read_csv(fights, low_memory=False)
    observations, _ = prepared_rows(raw)
    if observations.empty:
        raise ValueError("No completed fights found")
    train = observations[observations.event_date < train_end]
    validation = observations[(observations.event_date >= train_end) &
                              (observations.event_date < valid_end)]
    test = observations[observations.event_date >= valid_end]
    if min(len(train), len(validation), len(test)) < 20:
        raise ValueError("Each chronological split needs >=20 completed fights")
    model = train_model(train)
    validation_probability = model.predict_proba(validation[FEATURES].to_numpy(float))[:, 1]
    test_probability = model.predict_proba(test[FEATURES].to_numpy(float))[:, 1]
    elo_probability = 1 / (1 + 10 ** (-test.elo_diff.to_numpy(float)))
    report = dict(train_n=len(train),
                  validation=metrics(validation.y.to_numpy(int), validation_probability),
                  test=metrics(test.y.to_numpy(int), test_probability),
                  test_elo_baseline=metrics(test.y.to_numpy(int), elo_probability),
                  market_baseline=market_comparison(test, test_probability),
                  opening_odds_backtest=roi_report(test, test_probability),
                  limitations=["No independent calibration yet",
                               "No documented weight-cut observations yet",
                               "KO/TKO is a proxy, not a brain-injury diagnosis",
                               "Historical opening odds may not have been executable"])
    path = Path(out_dir)
    path.mkdir(parents=True, exist_ok=True)
    (path / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    predictions = test[["event_date", "f1_name", "f2_name", "y"]].copy()
    predictions["p_f1"] = test_probability
    predictions.to_csv(path / "out_of_sample_predictions.csv", index=False)
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fights", default="data/ufc_all_fights_wide.csv")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()
    f = Path(args.fights)
    if args.download:
        f.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(DATA_URL, f)
    print(json.dumps(run(f, args.out), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

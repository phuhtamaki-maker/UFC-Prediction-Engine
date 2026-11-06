"""Causal UFC striking/wrestling profiles from already completed fights.

Never feed target-bout fight statistics into its own features. Accumulate stats
only AFTER all bouts on a calendar date have been snapshotted. Missing stats
are not silently treated as successful or unsuccessful actions.
"""
import math

SKILL_FEATURES = [
    "sig_strikes_per_min_diff",
    "sig_strike_defense_diff",
    "takedowns_per_15min_diff",
    "takedown_defense_diff",
]

def number(v):
    try:
        x = float(v)
        return x if math.isfinite(x) and x >= 0 else None
    except (TypeError, ValueError):
        return None

def state():
    return {"sig_landed": 0., "sig_minutes": 0.,
            "sig_defended": 0., "sig_faced": 0.,
            "td_landed": 0., "td_minutes": 0.,
            "td_defended": 0., "td_faced": 0.,
            "sampled_bouts": 0}

def snapshot(s):
    """Predeclared shrinkage priors; use observed exposures only."""
    return {
        "sig_strikes_per_min": (s["sig_landed"] + 12) / (s["sig_minutes"] + 4),
        "sig_strike_defense": (s["sig_defended"] + 20) / (s["sig_faced"] + 40),
        "takedowns_per_15min": 15 * (s["td_landed"] + 0.5) / (s["td_minutes"] + 5),
        "takedown_defense": (s["td_defended"] + 5) / (s["td_faced"] + 10),
    }

def update(s, row, slot):
    """Call only after bout's pre-fight snapshots were taken."""
    other = 2 if slot == 1 else 1
    duration = number(row.get("fight_duration_sec"))
    seconds_ok = duration is not None and 0 < duration <= 25 * 60
    own_sig = number(row.get(f"f{slot}_tot_sig_str_landed"))
    incoming_sig = number(row.get(f"f{other}_tot_sig_str_landed"))
    incoming_sig_att = number(row.get(f"f{other}_tot_sig_str_att"))
    own_td = number(row.get(f"f{slot}_tot_td_landed"))
    incoming_td = number(row.get(f"f{other}_tot_td_landed"))
    incoming_td_att = number(row.get(f"f{other}_tot_td_att"))
    updated = False
    if seconds_ok and own_sig is not None:
        s["sig_landed"] += own_sig
        s["sig_minutes"] += duration / 60
        updated = True
    if incoming_sig is not None and incoming_sig_att is not None and incoming_sig <= incoming_sig_att:
        s["sig_defended"] += incoming_sig_att - incoming_sig
        s["sig_faced"] += incoming_sig_att
        updated = True
    if seconds_ok and own_td is not None:
        s["td_landed"] += own_td
        s["td_minutes"] += duration / 60
        updated = True
    if incoming_td is not None and incoming_td_att is not None and incoming_td <= incoming_td_att:
        s["td_defended"] += incoming_td_att - incoming_td
        s["td_faced"] += incoming_td_att
        updated = True
    if updated:
        s["sampled_bouts"] += 1

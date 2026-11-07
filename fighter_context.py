"""Structured ledger of *publicly documented*, time-stamped fighter availability news.

No diagnosis, private records, speculation, or unverified personal-life rumors.
Observations are context only; they do NOT change win probabilities until a
historical out-of-sample validation establishes an effect.
"""
from __future__ import annotations
import csv
import datetime as dt
from pathlib import Path
from urllib.parse import urlparse


ALLOWED_CATEGORIES = {
    "official_medical_suspension",
    "public_injury_announcement",
    "missed_weight",
    "short_notice",
    "public_camp_change",
    "travel_disruption",
    "fight_cancellation",
    "official_weigh_in",
}
ALLOWED_SOURCES = {"official_commission", "ufc", "athlete_public_statement", "reputable_news"}


def parse_date(text):
    """Accept an exact ISO calendar date or timezone-aware ISO timestamp.

    Never silently truncate malformed strings or accept naive timestamps:
    publication timing must be independently auditable.
    """
    value = str(text).strip()
    if len(value) == 10:
        return dt.date.fromisoformat(value)
    if "T" not in value:
        raise ValueError("Expected ISO date or timezone-aware timestamp")
    timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Publication timestamp requires an explicit timezone")
    return timestamp.astimezone(dt.timezone.utc).date()


def verified_observations(path, bout_date):
    """Return only documented observations published BEFORE bout date.

    CSV columns: fighter,category,published_date,source_url,source_type,note.
    Avoid private medical data, conjecture, unverifiable family issues.
    The dates must be SOURCE publication dates, not database import dates.
    """
    day = parse_date(bout_date)
    if not Path(path).exists():
        raise FileNotFoundError(path)
    accepted = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"fighter", "category", "published_date", "source_url", "source_type", "note"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required public-observation CSV columns")
        for row in reader:
            fighter = str(row["fighter"]).strip()
            category = str(row["category"]).strip()
            source_type = str(row["source_type"]).strip()
            url = str(row["source_url"]).strip()
            date = parse_date(row["published_date"])
            host = urlparse(url)
            if not fighter or category not in ALLOWED_CATEGORIES:
                continue
            if source_type not in ALLOWED_SOURCES:
                continue
            if host.scheme != "https" or not host.netloc or not host.netloc.count("."):
                continue
            if date >= day:
                continue
            accepted.append({key: str(row[key]).strip() for key in required})
    return accepted

"""Regression tests for unambiguous scoring dates (issue #17)."""
import pytest

from score_frozen import key, strict_event_date


@pytest.mark.parametrize("bad", [
    "07-11-2026", "11/07/2026", "20261107", "2026-11-07T00:00:00",
    "2026-1-07", "2026-02-29", "２０２６-11-07", "",
])
def test_reject_noncanonical_event_dates(bad):
    with pytest.raises(ValueError):
        strict_event_date(bad)


def test_accept_canonical_event_date_and_order_independent_key():
    assert strict_event_date("2026-11-07") == "2026-11-07"
    assert key("2026-11-07", "Fighter A", "Fighter B") == key(
        "2026-11-07", "Fighter B", "Fighter A"
    )

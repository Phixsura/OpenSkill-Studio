"""Metrics day key function tests."""

from app.services.app_metrics import _day_key
from datetime import date


def test_day_key_format():
    key = _day_key()
    # Should be YYYY-MM-DD format
    assert len(key) == 10
    assert key.count("-") == 2

def test_day_key_matches_today():
    key = _day_key()
    today = date.today().isoformat()
    assert key == today

def test_day_key_deterministic():
    assert _day_key() == _day_key()

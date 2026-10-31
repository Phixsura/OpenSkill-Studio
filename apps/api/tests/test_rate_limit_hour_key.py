"""Rate limit hour key tests."""

from app.services.app_rate_limit import _hour_key
from datetime import datetime, timezone

def test_hour_key_format():
    key = _hour_key()
    assert len(key) >= 13  # YYYY-MM-DD-HH minimum

def test_hour_key_deterministic():
    assert _hour_key() == _hour_key()

def test_hour_key_is_string():
    assert isinstance(_hour_key(), str)

def test_hour_key_contains_date():
    key = _hour_key()
    # Should contain year
    year = str(datetime.now(timezone.utc).year)
    assert year in key or str(datetime.now().year) in key

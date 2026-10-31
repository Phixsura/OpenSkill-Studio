from app.services.app_marketplace_app_app_date_formatter import format_relative, format_duration

def test_relative_old():
    r = format_relative(timestamp="2020-01-01T00:00:00Z")
    assert "2020" in r["relative"]  # shows absolute date for old

def test_invalid():
    r = format_relative(timestamp="not-a-date")
    assert "error" in r

def test_duration_seconds():
    assert format_duration(seconds=45) == "45s"

def test_duration_minutes():
    assert format_duration(seconds=125) == "2m 5s"

def test_duration_hours():
    assert format_duration(seconds=3725) == "1h 2m"

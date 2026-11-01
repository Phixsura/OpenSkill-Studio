from app.services.app_marketplace_date_formatter import format_relative_time, format_date_short, format_date_range

def test_old_date():
    r = format_relative_time(iso_date="2020-01-01T00:00:00Z")
    assert "y ago" in r

def test_invalid():
    r = format_relative_time(iso_date="not-a-date")
    assert r == "not-a-date"

def test_short():
    r = format_date_short(iso_date="2026-06-15T10:00:00Z")
    assert "Jun" in r
    assert "2026" in r

def test_range():
    r = format_date_range(start="2026-01-01T00:00:00Z", end="2026-12-31T00:00:00Z")
    assert "Jan" in r
    assert "Dec" in r
    assert "—" in r

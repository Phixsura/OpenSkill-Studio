from app.services.app_marketplace_app_app_date_range_picker import resolve_date_range

def test_7d():
    r = resolve_date_range(preset="7d", now="2026-10-23T12:00:00")
    assert r["days"] == 7
    assert r["label"] == "Last 7 days"

def test_30d():
    r = resolve_date_range(preset="30d", now="2026-10-23T12:00:00")
    assert r["days"] == 30

def test_today():
    r = resolve_date_range(preset="today", now="2026-10-23T15:30:00")
    assert r["days"] == 0

def test_invalid():
    r = resolve_date_range(preset="forever")
    assert "error" in r

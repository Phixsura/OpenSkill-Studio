from app.services.app_marketplace_app_app_time_ago import time_ago

def test_just_now():
    r = time_ago(timestamp="2026-10-23T12:00:00", now="2026-10-23T12:00:30")
    assert r["text"] == "just now"

def test_minutes():
    r = time_ago(timestamp="2026-10-23T12:00:00", now="2026-10-23T12:45:00")
    assert r["text"] == "45m ago"

def test_hours():
    r = time_ago(timestamp="2026-10-23T06:00:00", now="2026-10-23T12:00:00")
    assert r["text"] == "6h ago"

def test_days():
    r = time_ago(timestamp="2026-10-20T12:00:00", now="2026-10-23T12:00:00")
    assert r["text"] == "3d ago"

def test_months():
    r = time_ago(timestamp="2026-07-23T12:00:00", now="2026-10-23T12:00:00")
    assert "3mo ago" in r["text"]

from app.services.app_marketplace_app_app_app_app_app_app_app_dev_calendar import build_calendar, upcoming_events

def test_calendar():
    r = build_calendar([
        {"title": "v4.0 Launch", "date": "2026-11-01", "type": "release"},
        {"title": "DevCon 2026", "date": "2026-12-15", "type": "hackathon"},
        {"title": "API Freeze", "date": "2026-11-20", "type": "deadline"},
    ])
    assert r["total"] == 3
    assert "2026-11" in r["months"]
    assert len(r["by_month"]["2026-11"]) == 2

def test_upcoming():
    events = [
        {"title": "A", "date": "2026-10-01"},
        {"title": "B", "date": "2026-11-01"},
        {"title": "C", "date": "2026-12-01"},
    ]
    r = upcoming_events(events, after_date="2026-10-15", limit=2)
    assert len(r) == 2
    assert r[0]["title"] == "B"

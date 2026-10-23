from app.services.app_marketplace_app_maintenance_window import schedule_maintenance, get_upcoming_windows

def test_schedule():
    r = schedule_maintenance(app_id="a1", title="DB Migration",
        start_time="2026-11-01T03:00:00", duration_min=60, affected=["database", "api"])
    assert r["window_id"].startswith("mw_")
    assert r["status"] == "scheduled"
    assert len(r["affected_components"]) == 2

def test_invalid_duration():
    r = schedule_maintenance(app_id="a1", title="X", start_time="2026-11-01T00:00:00",
        duration_min=1000, affected=["api"])
    assert "error" in r

def test_upcoming():
    windows = [
        {"start_time": "2099-01-01T00:00:00", "end_time": "2099-01-01T01:00:00"},
    ]
    r = get_upcoming_windows(windows=windows)
    assert r["total_upcoming"] == 1
    assert not r["currently_in_maintenance"]

from app.services.app_marketplace_app_app_maintenance_window import create_maintenance, build_maintenance_schedule

def test_create_scheduled():
    r = create_maintenance(title="DB Migration", start="2099-01-01T02:00:00Z",
                           duration_min=120, services=["database", "api"])
    assert r["status"] == "scheduled"
    assert r["duration_min"] == 120
    assert "database" in r["services"]

def test_completed():
    r = create_maintenance(title="Past", start="2020-01-01T00:00:00Z", duration_min=30)
    assert r["status"] == "completed"

def test_schedule():
    windows = [
        {"title": "A", "status": "scheduled"},
        {"title": "B", "status": "in_progress"},
        {"title": "C", "status": "completed"},
    ]
    r = build_maintenance_schedule(windows=windows)
    assert r["upcoming"] == 1
    assert r["active"] == 1
    assert r["has_active"]

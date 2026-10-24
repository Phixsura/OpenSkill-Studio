from app.services.app_marketplace_app_app_app_app_app_app_app_incident_timeline import build_timeline, calculate_mttr

def test_timeline():
    r = build_timeline([
        {"timestamp": 3, "phase": "resolve", "msg": "fixed"},
        {"timestamp": 1, "phase": "detect", "msg": "alert fired"},
        {"timestamp": 2, "phase": "triage", "msg": "team paged"},
    ])
    assert r["total_events"] == 3
    assert r["events"][0]["timestamp"] == 1
    assert r["phases"]["detect"] == 1

def test_mttr():
    r = calculate_mttr([
        {"detected_at": 1000, "resolved_at": 1600},
        {"detected_at": 2000, "resolved_at": 3800},
    ])
    assert r["resolved_count"] == 2
    assert r["mttr_minutes"] == 20.0

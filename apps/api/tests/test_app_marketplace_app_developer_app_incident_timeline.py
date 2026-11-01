from app.services.app_marketplace_app_developer_app_incident_timeline import build_incident_timeline, compute_mttr

def test_timeline():
    incident = {"id": "inc1", "title": "API Down", "created_at": "2026-01-01T10:00:00Z",
                "resolved_at": "2026-01-01T10:30:00Z", "severity": "critical"}
    updates = [{"timestamp": "2026-01-01T10:10:00Z", "type": "update", "message": "Investigating", "author": "u1"}]
    t = build_incident_timeline(incident=incident, updates=updates)
    assert t["event_count"] == 3
    assert t["duration_minutes"] == 30

def test_unresolved():
    incident = {"id": "inc2", "title": "Slow", "created_at": "2026-01-01T10:00:00Z"}
    t = build_incident_timeline(incident=incident, updates=[])
    assert t["duration_minutes"] is None

def test_mttr():
    incidents = [
        {"created_at": "2026-01-01T10:00:00Z", "resolved_at": "2026-01-01T10:30:00Z"},
        {"created_at": "2026-01-02T10:00:00Z", "resolved_at": "2026-01-02T11:00:00Z"},
    ]
    r = compute_mttr(incidents=incidents)
    assert r["mttr_minutes"] == 45.0
    assert r["incident_count"] == 2

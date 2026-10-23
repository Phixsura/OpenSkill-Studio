from app.services.app_marketplace_app_app_app_incident_page import build_incident_page

def test_active():
    incident = {
        "title": "API Latency Spike", "severity": "major", "status": "identified",
        "affected_services": ["API", "Webhooks"], "created_at": "2026-10-24T10:00:00Z",
        "updates": [
            {"status": "investigating", "message": "Looking into it", "timestamp": "2026-10-24T10:05:00Z"},
            {"status": "identified", "message": "Found the root cause", "timestamp": "2026-10-24T10:30:00Z"},
        ],
    }
    r = build_incident_page(incident=incident)
    assert r["title"] == "API Latency Spike"
    assert r["status_icon"] == "🎯"
    assert len(r["timeline"]) == 2
    assert not r["is_resolved"]

def test_resolved():
    r = build_incident_page(incident={"title": "X", "status": "resolved", "resolved_at": "2026-10-24"})
    assert r["is_resolved"]

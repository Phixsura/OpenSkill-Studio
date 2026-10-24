from app.services.app_marketplace_app_app_app_app_app_app_app_postmortem import generate_postmortem, incident_stats

def test_generate():
    r = generate_postmortem({
        "title": "API Outage", "severity": "critical",
        "detected_at": 1000, "resolved_at": 2800,
        "affected_users": 5000, "services": ["api", "db"],
        "root_cause": "Database connection pool exhausted",
        "action_items": ["Increase pool size", "Add monitoring"],
        "timeline": [{"time": 1000, "event": "Alert fired"}],
    })
    assert r["duration_minutes"] == 30.0
    assert r["severity"] == "critical"
    assert r["impact"]["users_affected"] == 5000
    assert r["status"] == "completed"

def test_stats():
    r = incident_stats([
        {"severity": "critical", "duration_minutes": 30},
        {"severity": "medium", "duration_minutes": 10},
        {"severity": "critical", "duration_minutes": 60},
    ])
    assert r["total"] == 3
    assert r["by_severity"]["critical"] == 2

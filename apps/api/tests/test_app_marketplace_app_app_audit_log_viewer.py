from app.services.app_marketplace_app_app_audit_log_viewer import build_audit_log

EVENTS = [
    {"id": "1", "action": "login", "actor": "alice", "severity": "info", "timestamp": "2026-01-02T00:00:00Z"},
    {"id": "2", "action": "delete_app", "actor": "bob", "severity": "critical", "timestamp": "2026-01-01T00:00:00Z"},
    {"id": "3", "action": "update_settings", "actor": "alice", "severity": "warning", "timestamp": "2026-01-01T12:00:00Z"},
]

def test_all():
    r = build_audit_log(events=EVENTS)
    assert r["total"] == 3
    assert r["events"][0]["id"] == "1"  # newest first
    assert r["by_severity"]["critical"] == 1

def test_filter():
    r = build_audit_log(events=EVENTS, filter_severity="critical")
    assert r["total"] == 1
    assert r["events"][0]["action"] == "delete_app"

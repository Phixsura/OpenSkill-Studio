from app.services.app_marketplace_app_app_app_app_app_audit_log_page import build_audit_log_page

def test_audit():
    events = [
        {"action": "login", "actor": "Alice", "target": "", "ip": "1.2.3.4", "timestamp": "2026-10-01"},
        {"action": "create_app", "actor": "Alice", "target": "SuperApp", "timestamp": "2026-10-01"},
        {"action": "login", "actor": "Bob", "timestamp": "2026-10-02"},
    ]
    r = build_audit_log_page(events=events)
    assert r["total"] == 3
    assert len(r["available_actors"]) == 2

def test_filter():
    events = [{"action": "login", "actor": "Alice"}, {"action": "deploy", "actor": "Bob"}]
    r = build_audit_log_page(events=events, filter_action="login")
    assert r["total"] == 1

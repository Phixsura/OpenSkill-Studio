from app.services.app_marketplace_app_marketplace_admin_v2 import build_admin_dashboard_v2

def test_admin():
    d = build_admin_dashboard_v2(
        stats={"total_apps": 500},
        moderation_queue=[{"status": "pending"}, {"status": "reviewed"}],
        flagged_content=[{"id": "f1"}],
        system_alerts=[{"severity": "critical"}, {"severity": "warning"}])
    assert d["overview"]["pending_moderation"] == 1
    assert d["overview"]["critical_alerts"] == 1
    assert d["needs_attention"]

def test_clean():
    d = build_admin_dashboard_v2(stats={}, moderation_queue=[], flagged_content=[], system_alerts=[])
    assert not d["needs_attention"]

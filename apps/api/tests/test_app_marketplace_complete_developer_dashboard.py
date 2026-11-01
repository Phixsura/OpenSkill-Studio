from app.services.app_marketplace_complete_developer_dashboard import build_complete_developer_dashboard

def test_dashboard():
    d = build_complete_developer_dashboard(
        developer={"display_name": "DevCo", "verified": True},
        apps=[{"id": "a1", "name": "App1", "status": "published", "install_count": 200},
              {"id": "a2", "name": "App2", "status": "draft", "install_count": 0}],
        notifications=[{"read": False}, {"read": True}],
        analytics={"api_calls": 5000},
        team=[{"user_id": "u1"}, {"user_id": "u2"}],
        onboarding={"progress_pct": 80})
    assert d["page_type"] == "developer_dashboard"
    assert d["overview"]["total_apps"] == 2
    assert d["overview"]["published_apps"] == 1
    assert d["overview"]["total_installs"] == 200
    assert d["overview"]["unread_notifications"] == 1
    assert len(d["quick_actions"]) == 3

def test_empty():
    d = build_complete_developer_dashboard(
        developer={"display_name": "New"}, apps=[], notifications=[],
        analytics={}, team=[], onboarding={"progress_pct": 0})
    assert d["overview"]["total_apps"] == 0

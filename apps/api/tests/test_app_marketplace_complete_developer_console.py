from app.services.app_marketplace_complete_developer_console import build_complete_developer_console

def test_console():
    c = build_complete_developer_console(
        developer={"display_name": "DevCo", "verified": True},
        apps=[{"id": "a1", "name": "App", "status": "published", "install_count": 500}],
        analytics={"api_calls": 10000}, notifications=[{"read": False}, {"read": True}],
        team=[{"id": "u1"}, {"id": "u2"}], onboarding={"complete": False, "progress_pct": 60},
        billing={"plan": "pro"}, alerts=[{"triggered": True}, {"triggered": False}])
    assert c["page_type"] == "developer_console"
    assert c["dashboard"]["apps"]["published"] == 1
    assert c["dashboard"]["alerts"]["active"] == 1
    assert c["dashboard"]["notifications"]["unread"] == 1
    assert len(c["navigation"]) == 8
    assert c["onboarding"] is not None

def test_complete_onboarding():
    c = build_complete_developer_console(
        developer={"display_name": "X"}, apps=[], analytics={},
        notifications=[], team=[], onboarding={"complete": True},
        billing={}, alerts=[])
    assert c["onboarding"] is None

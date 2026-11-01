from app.services.app_marketplace_app_app_app_app_app_app_app_app_account_page import build_account_page

def test_account():
    user = {"name": "Alice Chen", "email": "alice@example.com", "bio": "Builder",
            "two_factor": True, "timezone": "America/New_York"}
    sessions = [{"id": "s1"}, {"id": "s2"}]
    connections = [{"provider": "GitHub", "connected": True, "username": "alicecode"}]
    r = build_account_page(user=user, sessions=sessions, connected_accounts=connections)
    assert r["profile"]["name"] == "Alice Chen"
    assert r["security"]["two_factor_enabled"]
    assert r["security"]["active_sessions"] == 2
    assert r["connected_count"] == 1
    assert len(r["sections"]) == 5

from app.services.app_marketplace_complete_dev_settings import build_complete_developer_settings

def test_settings():
    p = build_complete_developer_settings(
        profile={"display_name": "DevCo", "slug": "devco", "email": "dev@co.com", "completeness_pct": 80},
        security={"2fa_enabled": True, "active_sessions": 2},
        notifications={"email_digest": "weekly"},
        api_keys=[{"name": "prod"}, {"name": "staging"}],
        connected_accounts=[{"provider": "github"}],
        data_export={"last_export": "2026-10-01"})
    assert p["tab_count"] == 7
    assert p["tabs"][0]["data"]["completeness"] == 80
    assert p["tabs"][1]["data"]["two_factor"]
    assert p["tabs"][3]["title"] == "API Keys (2)"

def test_minimal():
    p = build_complete_developer_settings(
        profile={}, security={}, notifications={}, api_keys=[], connected_accounts=[], data_export=None)
    assert p["tabs"][5]["data"]["export_available"] is False

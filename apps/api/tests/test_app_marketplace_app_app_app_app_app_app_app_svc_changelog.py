from app.services.app_marketplace_app_app_app_app_app_app_app_svc_changelog import build_changelog

def test_changelog():
    r = build_changelog([
        {"version": "2.0", "type": "feat", "description": "Dark mode"},
        {"version": "2.0", "type": "fix", "description": "Login bug"},
        {"version": "1.0", "type": "feat", "description": "Initial release"},
    ])
    assert r["version_count"] == 2
    assert len(r["versions"]["2.0"]) == 2

from app.services.app_marketplace_app_app_app_app_app_app_app_update_notifier import check_updates, build_update_summary

def test_updates():
    r = check_updates([
        {"name": "Slack Bot", "installed_version": "2.0", "latest_version": "2.1", "icon": "💬"},
        {"name": "GitHub Sync", "installed_version": "1.5", "latest_version": "1.5"},
        {"name": "Analytics", "installed_version": "3.0", "latest_version": "4.0", "breaking": True},
    ])
    assert r["count"] == 2
    assert r["has_breaking"]
    assert not r["all_current"]

def test_summary():
    assert "up to date" in build_update_summary([])
    assert "2 updates" in build_update_summary([{"breaking": False}, {"breaking": True}])
    assert "1 breaking" in build_update_summary([{"breaking": False}, {"breaking": True}])

from app.services.app_marketplace_app_dependency_update import check_updates

def test_updates():
    deps = [
        {"name": "react", "current_version": "18.2.0", "latest_version": "18.3.0"},
        {"name": "next", "current_version": "14.0.0", "latest_version": "15.1.0"},
        {"name": "tailwind", "current_version": "3.4.0", "latest_version": "3.4.0"},
    ]
    r = check_updates(dependencies=deps)
    assert r["updates_available"] == 2
    assert r["breaking_count"] == 1  # next 14→15
    assert not r["up_to_date"]

def test_up_to_date():
    deps = [{"name": "lodash", "current_version": "4.17.21", "latest_version": "4.17.21"}]
    r = check_updates(dependencies=deps)
    assert r["up_to_date"]

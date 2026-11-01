from app.services.app_marketplace_app_app_app_dependency_update import check_updates

def test_updates():
    deps = [
        {"name": "react", "current": "18.2.0", "latest": "18.3.1"},
        {"name": "next", "current": "14.0.0", "latest": "15.0.0"},
        {"name": "lodash", "current": "4.17.21", "latest": "4.17.21"},
    ]
    r = check_updates(dependencies=deps)
    assert r["updates_available"] == 2
    assert r["breaking"] == 1
    assert not r["up_to_date"]
    assert r["dependencies"][0]["is_breaking"]  # next sorted first

def test_up_to_date():
    r = check_updates(dependencies=[{"name": "x", "current": "1.0.0", "latest": "1.0.0"}])
    assert r["up_to_date"]

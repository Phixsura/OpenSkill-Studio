from app.services.app_marketplace_app_app_app_app_app_app_app_dep_update import check_updates, prioritize_updates

def test_check():
    r = check_updates([
        {"name": "react", "current": "18.2.0", "latest": "19.0.0"},
        {"name": "axios", "current": "1.5.0", "latest": "1.6.0"},
        {"name": "lodash", "current": "4.17.21", "latest": "4.17.21"},
    ])
    assert r["outdated_count"] == 2
    assert r["up_to_date"] == 1
    assert r["has_major"]

def test_prioritize():
    outdated = [
        {"name": "a", "type": "patch"}, {"name": "b", "type": "major"}, {"name": "c", "type": "minor"},
    ]
    p = prioritize_updates(outdated)
    assert p[0]["type"] == "major"
    assert p[1]["type"] == "minor"

from app.services.app_marketplace_app_app_getting_started import build_getting_started

def test_partial():
    r = build_getting_started(developer_name="Alice", completed=["signup", "verify", "profile"])
    assert r["completed"] == 3
    assert r["pct"] == 38
    assert r["current_step"]["id"] == "create_app"
    assert not r["all_done"]

def test_all_done():
    all_ids = ["signup", "verify", "profile", "create_app", "add_sdk", "first_api", "deploy", "publish"]
    r = build_getting_started(developer_name="Bob", completed=all_ids)
    assert r["all_done"]
    assert r["remaining_time_min"] == 0

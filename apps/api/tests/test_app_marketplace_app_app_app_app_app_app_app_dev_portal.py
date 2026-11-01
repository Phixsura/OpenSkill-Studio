from app.services.app_marketplace_app_app_app_app_app_app_app_dev_portal import get_portal, portal_stats

def test_portal():
    r = get_portal(["sdk-setup", "first-app"])
    assert r["completed"] == 2
    assert r["progress_pct"] == 33
    assert r["remaining_time_min"] < r["total_time_min"]

def test_stats():
    r = portal_stats(5000, 300, 25_000_000)
    assert r["display_calls"] == "25.0M"

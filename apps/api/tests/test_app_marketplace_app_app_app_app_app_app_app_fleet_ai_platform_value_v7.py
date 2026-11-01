from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_value_v7 import fleet_ai_platform_value_v7
def test_pvv7():
    r = fleet_ai_platform_value_v7([{"active": True, "value_usd": 5000000000, "roi_pct": 500, "hours_saved": 10000000}])
    assert r["value_usd"] == 5000000000
    assert r["valuable"]

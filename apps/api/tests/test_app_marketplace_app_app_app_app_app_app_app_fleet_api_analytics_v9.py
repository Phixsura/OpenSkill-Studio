from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_analytics_v9 import fleet_api_analytics_v9
def test_aa_v9():
    r = fleet_api_analytics_v9([{"calls_today": 100000, "consumer": "web", "avg_ms": 25}])
    assert r["calls_today"] == 100000
    assert r["healthy"]

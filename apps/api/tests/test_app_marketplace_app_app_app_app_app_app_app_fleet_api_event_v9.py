from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_event_v9 import fleet_api_event_v9
def test_aev_v9():
    r = fleet_api_event_v9([{"published_today": 10000, "consumed_today": 10000, "failed": 0}])
    assert r["published_today"] == 10000
    assert r["healthy"]

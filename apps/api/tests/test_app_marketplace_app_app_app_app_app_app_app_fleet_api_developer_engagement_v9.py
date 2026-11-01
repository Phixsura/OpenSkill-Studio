from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_developer_engagement_v9 import fleet_api_developer_engagement_v9
def test_ade2_v9():
    r = fleet_api_developer_engagement_v9([{"active_devs": 1000, "calls_per_dev": 500, "nps": 85}])
    assert r["active_developers"] == 1000
    assert r["healthy"]

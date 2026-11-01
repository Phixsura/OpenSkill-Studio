from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_traffic_spl import fleet_ai_traffic_split
def test_ts():
    r = fleet_ai_traffic_split([{"active": True, "splits": 10, "requests_24h": 100000000, "variants": 3}])
    assert r["splits"] == 10
    assert r["splitting"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_reliability_v9 import fleet_service_reliability_v9
def test_sr2_v9():
    r = fleet_service_reliability_v9([{"reliability_score": 99.99}])
    assert r["uptime_class"] == "99.99%"
    assert r["healthy"]

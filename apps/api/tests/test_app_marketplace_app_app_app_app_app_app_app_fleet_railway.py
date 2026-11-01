from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_railway import fleet_railway_status
def test_rw():
    r = fleet_railway_status([{"status": "SUCCESS", "deploys_24h": 5}, {"status": "SUCCESS", "deploys_24h": 3}])
    assert r["deploys_24h"] == 8
    assert r["all_healthy"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kserve import fleet_kserve_status
def test_ks():
    r = fleet_kserve_status([{"ready": True, "models": 20, "qps": 10000}])
    assert r["models"] == 20
    assert r["all_ready"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_weights import fleet_weights_status
def test_wt():
    r = fleet_weights_status([{"active": True, "models": 100, "versions": 500, "storage_tb": 10}])
    assert r["models"] == 100
    assert r["versions"] == 500

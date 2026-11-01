from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_xata import fleet_xata_status
def test_xata():
    r = fleet_xata_status([{"active": True, "branches": 5, "records": 1000000}])
    assert r["records"] == 1000000
    assert r["all_active"]

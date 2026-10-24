from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hex import fleet_hex_status
def test_hex():
    r = fleet_hex_status([{"active": True, "projects": 100, "runs_24h": 5000}])
    assert r["projects"] == 100
    assert r["all_active"]

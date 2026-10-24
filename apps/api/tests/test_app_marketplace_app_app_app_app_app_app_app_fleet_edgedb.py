from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_edgedb import fleet_edgedb_status
def test_edb():
    r = fleet_edgedb_status([{"available": True, "branches": 5, "types": 80}])
    assert r["types"] == 80
    assert r["all_available"]

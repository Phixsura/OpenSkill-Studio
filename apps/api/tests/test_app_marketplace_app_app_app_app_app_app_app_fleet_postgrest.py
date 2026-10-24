from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_postgrest import fleet_postgrest_status
def test_prest():
    r = fleet_postgrest_status([{"running": True, "rps": 50000, "schemas": 5}])
    assert r["rps"] == 50000
    assert r["all_running"]

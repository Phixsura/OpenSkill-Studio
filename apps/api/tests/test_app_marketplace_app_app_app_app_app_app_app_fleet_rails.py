from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rails import fleet_rails_status
def test_rails():
    r = fleet_rails_status([{"running": True, "rps": 10000, "db_pool_pct": 60}])
    assert r["rps"] == 10000
    assert r["healthy"]

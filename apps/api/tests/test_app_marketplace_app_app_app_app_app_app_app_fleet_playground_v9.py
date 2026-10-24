from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_playground_v9 import fleet_playground_v9
def test_pg_v9():
    r = fleet_playground_v9([{"active": True, "cpu_hours": 8}])
    assert r["active"] == 1
    assert r["healthy"]

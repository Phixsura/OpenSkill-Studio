from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_turso import fleet_turso_status
def test_turso():
    r = fleet_turso_status([{"replicas": 5, "rows": 1000000, "locations": ["us", "eu", "ap"]}])
    assert r["locations"] == 3
    assert r["globally_distributed"]

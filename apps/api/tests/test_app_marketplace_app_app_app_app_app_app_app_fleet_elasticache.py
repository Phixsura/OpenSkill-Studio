from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_elasticache import fleet_elasticache_status
def test_ec():
    r = fleet_elasticache_status([{"status": "available", "nodes": 6, "memory_pct": 65}])
    assert r["nodes"] == 6
    assert r["healthy"]

from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_conn_pool import monitor_pools, pool_recommendation

def test_monitor():
    r = monitor_pools([
        {"service": "api", "destination": "db", "active": 18, "max_size": 20},
        {"service": "api", "destination": "cache", "active": 5, "max_size": 20},
    ])
    assert r["saturated"] == 1
    assert r["healthy"] == 1

def test_recommendation():
    r = pool_recommendation({"util_pct": 95})
    assert r["action"] == "increase_pool_size"
    r2 = pool_recommendation({"util_pct": 10})
    assert r2["action"] == "decrease_pool_size"

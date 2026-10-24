from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_conn_pool import fleet_ai_connection_pool
def test_cp():
    r = fleet_ai_connection_pool([{"active": True, "max_connections": 1000, "active_connections": 600}])
    assert r["utilization"] == 60.0
    assert r["healthy"]

from app.services.app_marketplace_app_app_app_app_app_app_app_db_conn_mon import monitor_connections, connection_trend

def test_monitor():
    r = monitor_connections([
        {"name": "primary", "active": 15, "max_size": 20},
        {"name": "replica", "active": 5, "max_size": 20},
        {"name": "analytics", "active": 19, "max_size": 20},
    ])
    assert r["total_active"] == 39
    assert r["utilization_pct"] == 65.0
    assert "analytics" in r["saturated_pools"]
    assert not r["healthy"]

def test_trend():
    r = connection_trend([{"active": 10}, {"active": 20}])
    assert r["trend"] == "increasing"
    assert r["delta"] == 10

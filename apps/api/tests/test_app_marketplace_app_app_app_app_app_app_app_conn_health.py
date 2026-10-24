from app.services.app_marketplace_app_app_app_app_app_app_app_conn_health import check_connections

def test_check():
    r = check_connections([
        {"name": "postgres", "type": "database", "latency_ms": 5, "timeout_ms": 1000, "reachable": True},
        {"name": "redis", "type": "cache", "latency_ms": 2, "timeout_ms": 500, "reachable": True},
        {"name": "external-api", "type": "http", "latency_ms": 6000, "timeout_ms": 5000, "reachable": True},
    ])
    assert r["healthy"] == 2
    assert not r["all_healthy"]
    assert r["connections"][2]["error"] == ""  # no error msg in input

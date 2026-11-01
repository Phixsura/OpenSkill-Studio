from app.services.app_marketplace_app_app_app_app_app_app_app_topo_health import topology_health_summary

def test_healthy():
    r = topology_health_summary(
        [{"name": "api", "health": "healthy"}, {"name": "db", "health": "healthy"}],
        [{"source": "api", "dest": "db", "health": "healthy", "on_critical_path": True}])
    assert r["overall"] == "healthy"
    assert r["node_health_pct"] == 100.0

def test_critical():
    r = topology_health_summary(
        [{"name": "api", "health": "healthy"}, {"name": "db", "health": "down"}],
        [{"source": "api", "dest": "db", "health": "down", "on_critical_path": True}])
    assert r["overall"] == "critical"
    assert r["critical_path_issues"] == 1

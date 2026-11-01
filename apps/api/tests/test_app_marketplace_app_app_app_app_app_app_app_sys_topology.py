from app.services.app_marketplace_app_app_app_app_app_app_app_sys_topology import build_system_topology

def test_topology():
    r = build_system_topology({
        "frontend": [{"name": "web", "status": "healthy", "connections": ["api"]}],
        "backend": [{"name": "api", "status": "healthy", "connections": ["db", "cache"]},
                     {"name": "worker", "status": "healthy", "connections": ["db"]}],
        "data": [{"name": "db", "status": "healthy"}, {"name": "cache", "status": "degraded"}],
    })
    assert r["total_services"] == 5
    assert r["layer_count"] == 3
    assert r["layers"]["backend"]["services"] == 2
    assert r["layers"]["data"]["healthy"] == 1

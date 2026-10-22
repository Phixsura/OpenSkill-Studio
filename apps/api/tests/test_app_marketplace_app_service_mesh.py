from app.services.app_marketplace_app_service_mesh import register_service, discover_service, build_service_topology

def test_register():
    s = register_service(service_id="s1", name="api", endpoints=["https://api:8000"], version="1.0")
    assert s["status"] == "registered"

def test_discover():
    registry = [{"name": "api", "health": "healthy", "service_id": "s1"},
                {"name": "api", "health": "unhealthy", "service_id": "s2"}]
    r = discover_service(name="api", registry=registry)
    assert r["service_id"] == "s1"

def test_discover_none():
    assert discover_service(name="missing", registry=[]) is None

def test_topology():
    services = [{"service_id": "s1", "name": "api"}, {"service_id": "s2", "name": "worker"}]
    connections = [{"from": "s1", "to": "s2"}]
    t = build_service_topology(services=services, connections=connections)
    assert t["service_count"] == 2
    assert t["connection_count"] == 1

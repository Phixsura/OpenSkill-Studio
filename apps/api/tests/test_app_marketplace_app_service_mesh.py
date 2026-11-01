from app.services.app_marketplace_app_service_mesh import build_service_topology, get_traffic_policy

def test_topology():
    services = [
        {"id": "api", "name": "API Gateway", "depends_on": ["auth", "catalog"]},
        {"id": "auth", "name": "Auth Service", "depends_on": ["db"]},
        {"id": "catalog", "name": "Catalog", "depends_on": ["db"]},
        {"id": "db", "name": "Database", "type": "datastore"},
    ]
    r = build_service_topology(services=services)
    assert r["total_services"] == 4
    assert r["total_connections"] == 4
    assert r["mesh_health"] == "healthy"

def test_degraded():
    services = [{"id": "a", "name": "A", "healthy": True}, {"id": "b", "name": "B", "healthy": False}]
    r = build_service_topology(services=services)
    assert r["mesh_health"] == "degraded"

def test_policy():
    r = get_traffic_policy(service_id="api")
    assert r["timeout_ms"] == 5000
    assert r["retry_policy"]["max_retries"] == 3

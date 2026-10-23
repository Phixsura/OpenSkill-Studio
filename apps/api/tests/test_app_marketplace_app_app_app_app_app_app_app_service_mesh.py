from app.services.app_marketplace_app_app_app_app_app_app_app_service_mesh import build_mesh

def test_mesh():
    services = [
        {"id": "gateway", "name": "API Gateway", "status": "healthy", "rps": 5000},
        {"id": "auth", "name": "Auth Service", "status": "healthy", "rps": 2000},
        {"id": "users", "name": "User Service", "status": "degraded", "rps": 1500},
        {"id": "billing", "name": "Billing", "status": "healthy", "rps": 500},
    ]
    connections = [
        {"from": "gateway", "to": "auth"}, {"from": "gateway", "to": "users"},
        {"from": "gateway", "to": "billing"}, {"from": "users", "to": "auth"},
    ]
    r = build_mesh(services, connections)
    assert r["total_services"] == 4
    assert r["total_connections"] == 4
    assert r["unhealthy_count"] == 1
    assert r["mesh_health"] == "degraded"
    assert r["critical_path"][0] == "gateway"

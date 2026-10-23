from app.services.app_marketplace_app_app_service_mesh import build_service_mesh

def test_mesh():
    services = [
        {"name": "api", "port": 8080, "dependencies": ["auth", "db"]},
        {"name": "auth", "port": 8081, "dependencies": ["db"]},
        {"name": "db", "port": 5432, "protocol": "tcp", "dependencies": []},
    ]
    policies = [{"source": "api", "destination": "auth", "mtls": True}]
    r = build_service_mesh(services=services, policies=policies)
    assert r["service_count"] == 3
    assert r["total_connections"] == 3
    assert r["mtls_enabled"]
    assert r["services"][0]["dep_count"] == 2

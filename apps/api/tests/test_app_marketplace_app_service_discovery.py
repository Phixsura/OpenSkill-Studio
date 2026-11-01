from app.services.app_marketplace_app_service_discovery import register_service, discover_service

def test_register():
    r = register_service(service_name="api", host="10.0.0.1", port=8080, tags=["v2"])
    assert r["instance_id"].startswith("api-")
    assert r["address"] == "10.0.0.1:8080"
    assert r["status"] == "healthy"

def test_invalid_port():
    r = register_service(service_name="x", host="x", port=99999)
    assert "error" in r

def test_discover():
    instances = [
        {"instance_id": "api-1", "status": "healthy", "address": "10.0.0.1:8080"},
        {"instance_id": "api-2", "status": "unhealthy", "address": "10.0.0.2:8080"},
    ]
    r = discover_service(service_name="api", instances=instances)
    assert r["selected"]["instance_id"] == "api-1"
    assert r["healthy_count"] == 1

def test_discover_none():
    r = discover_service(service_name="api", instances=[{"instance_id": "x", "status": "unhealthy"}])
    assert "error" in r

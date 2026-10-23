from app.services.app_marketplace_app_app_app_app_app_app_app_svc_discovery import (
    register_service, discover, discover_by_tag, deregister, registry_overview, clear_registry,
)

def test_register_discover():
    clear_registry()
    register_service("api", "10.0.0.1", 8080, tags=["http", "v2"])
    register_service("worker", "10.0.0.2", 9090, tags=["grpc"])
    r = discover("api")
    assert r["found"]
    assert r["address"] == "10.0.0.1:8080"
    by_tag = discover_by_tag("http")
    assert len(by_tag) == 1
    clear_registry()

def test_deregister():
    clear_registry()
    register_service("temp", "localhost", 3000)
    deregister("temp")
    assert not discover("temp")["found"]
    clear_registry()

def test_overview():
    clear_registry()
    register_service("a", "h", 1, tags=["x"])
    register_service("b", "h", 2, tags=["x", "y"])
    r = registry_overview()
    assert r["total"] == 2
    assert "x" in r["tags"]
    clear_registry()

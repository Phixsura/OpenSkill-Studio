from app.services.app_marketplace_app_app_app_app_app_app_app_svc_discovery import ServiceDiscovery

def test_register_discover():
    sd = ServiceDiscovery(heartbeat_ttl=60)
    sd.register("api", "10.0.0.1", 8080, ["http", "rest"])
    sd.register("worker", "10.0.0.2", 9090, ["grpc"])
    r = sd.discover(tag="http")
    assert len(r) == 1
    assert r[0]["name"] == "api"

def test_heartbeat():
    sd = ServiceDiscovery()
    sd.register("svc", "host", 80)
    r = sd.heartbeat("svc")
    assert r["alive"]
    r2 = sd.heartbeat("missing")
    assert not r2["alive"]

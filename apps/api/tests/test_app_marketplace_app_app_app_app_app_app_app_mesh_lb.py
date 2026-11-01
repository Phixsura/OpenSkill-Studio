from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_lb import MeshLoadBalancer

def test_round_robin():
    mlb = MeshLoadBalancer("round_robin")
    mlb.register_backends("api", [
        {"address": "10.0.0.1:8080", "healthy": True},
        {"address": "10.0.0.2:8080", "healthy": True},
    ])
    r1 = mlb.select("api")
    r2 = mlb.select("api")
    assert r1["backend"] != r2["backend"]

def test_least_conn():
    mlb = MeshLoadBalancer("least_conn")
    mlb.register_backends("api", [
        {"address": "a", "healthy": True, "connections": 10},
        {"address": "b", "healthy": True, "connections": 2},
    ])
    r = mlb.select("api")
    assert r["backend"] == "b"

def test_no_healthy():
    mlb = MeshLoadBalancer()
    mlb.register_backends("api", [{"address": "a", "healthy": False}])
    r = mlb.select("api")
    assert not r["selected"]

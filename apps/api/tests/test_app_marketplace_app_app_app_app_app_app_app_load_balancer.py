from app.services.app_marketplace_app_app_app_app_app_app_app_load_balancer import create_pool, select_backend

def test_pool():
    r = create_pool("api", "round_robin", [
        {"address": "10.0.0.1:8080", "weight": 3},
        {"address": "10.0.0.2:8080", "weight": 1, "healthy": False},
    ])
    assert r["created"]
    assert r["healthy"] == 1
    assert r["capacity_pct"] == 50

def test_select():
    pool = create_pool("api", "round_robin", [
        {"address": "a"}, {"address": "b"}, {"address": "c"},
    ])
    assert select_backend(pool, 0)["backend"] == "a"
    assert select_backend(pool, 1)["backend"] == "b"
    assert select_backend(pool, 3)["backend"] == "a"

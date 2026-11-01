from app.services.app_marketplace_app_app_app_app_app_app_app_lb_strategy import LoadBalancer

def test_round_robin():
    lb = LoadBalancer(["a", "b", "c"], "round_robin")
    results = [lb.next()["backend"] for _ in range(6)]
    assert results == ["a", "b", "c", "a", "b", "c"]

def test_hash_consistent():
    lb = LoadBalancer(["a", "b", "c"], "hash")
    r1 = lb.next(key="user-1")["backend"]
    r2 = lb.next(key="user-1")["backend"]
    assert r1 == r2  # same key → same backend

def test_weighted():
    lb = LoadBalancer(["a", "b"], "weighted")
    lb.set_weight("a", 3)
    lb.set_weight("b", 1)
    results = [lb.next()["backend"] for _ in range(4)]
    assert results.count("a") == 3
    assert results.count("b") == 1

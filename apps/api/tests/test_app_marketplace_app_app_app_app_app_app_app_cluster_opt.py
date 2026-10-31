from app.services.app_marketplace_app_app_app_app_app_app_app_cluster_opt import optimize_allocation

def test_optimal():
    r = optimize_allocation(
        [{"cpu": 8, "memory_gb": 32}, {"cpu": 8, "memory_gb": 32}],
        [{"cpu_request": 5, "memory_request_gb": 20}, {"cpu_request": 4, "memory_request_gb": 15}])
    assert r["recommendation"] == "optimal"

def test_over():
    r = optimize_allocation(
        [{"cpu": 32, "memory_gb": 128}],
        [{"cpu_request": 2, "memory_request_gb": 8}])
    assert r["recommendation"] == "scale_down"

def test_under():
    r = optimize_allocation(
        [{"cpu": 4, "memory_gb": 8}],
        [{"cpu_request": 3.5, "memory_request_gb": 7}])
    assert r["recommendation"] == "scale_up"

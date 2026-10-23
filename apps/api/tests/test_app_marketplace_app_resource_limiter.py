from app.services.app_marketplace_app_resource_limiter import get_resource_limits, check_resource_usage

def test_limits():
    r = get_resource_limits(plan="pro")
    assert r["limits"]["cpu_cores"] == 2
    assert not r["unlimited_bandwidth"]

def test_enterprise():
    r = get_resource_limits(plan="enterprise")
    assert r["unlimited_bandwidth"]

def test_within():
    r = check_resource_usage(plan="pro", usage={"cpu_cores": 1.5, "memory_mb": 1024})
    assert r["within_limits"]

def test_violation():
    r = check_resource_usage(plan="free", usage={"cpu_cores": 1.0, "memory_mb": 512})
    assert r["violation_count"] == 2
    assert not r["within_limits"]

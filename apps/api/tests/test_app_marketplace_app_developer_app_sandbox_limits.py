from app.services.app_marketplace_app_developer_app_sandbox_limits import get_sandbox_limits, check_sandbox_limits, estimate_plan_for_usage

def test_limits():
    l = get_sandbox_limits(plan="pro")
    assert l["memory_mb"] == 1024

def test_within():
    r = check_sandbox_limits(usage={"cpu_ms": 500, "memory_mb": 32}, plan="free")
    assert r["within_limits"]

def test_violation():
    r = check_sandbox_limits(usage={"cpu_ms": 5000, "memory_mb": 128}, plan="free")
    assert not r["within_limits"]
    assert len(r["violations"]) == 2

def test_estimate_free():
    assert estimate_plan_for_usage(usage={"cpu_ms": 500, "memory_mb": 32}) == "free"

def test_estimate_pro():
    assert estimate_plan_for_usage(usage={"cpu_ms": 10000, "memory_mb": 512}) == "pro"

def test_estimate_enterprise():
    assert estimate_plan_for_usage(usage={"cpu_ms": 999999}) == "enterprise"

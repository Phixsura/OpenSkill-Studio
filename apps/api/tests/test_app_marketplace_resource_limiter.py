from app.services.app_marketplace_resource_limiter import (
    ResourceLimiter, ResourceLimit, ResourceUsage,
)


def test_no_violations_under_limit():
    rl = ResourceLimiter()
    rl.set_limits("ext-1", ResourceLimit(cpu_percent=80, memory_mb=256))
    rl.update_usage("ext-1", ResourceUsage(cpu_percent=30, memory_mb=100))
    violations = rl.check("ext-1")
    assert len(violations) == 0


def test_warn_at_80_percent():
    rl = ResourceLimiter()
    rl.set_limits("ext-2", ResourceLimit(memory_mb=100))
    rl.update_usage("ext-2", ResourceUsage(memory_mb=85))
    violations = rl.check("ext-2")
    mem_v = [v for v in violations if v["resource"] == "memory"]
    assert len(mem_v) == 1
    assert mem_v[0]["action"] == "warn"


def test_throttle_at_90_percent():
    rl = ResourceLimiter()
    rl.set_limits("ext-3", ResourceLimit(cpu_percent=100))
    rl.update_usage("ext-3", ResourceUsage(cpu_percent=95))
    violations = rl.check("ext-3")
    assert any(v["action"] == "throttle" for v in violations)


def test_terminate_at_limit():
    rl = ResourceLimiter()
    rl.set_limits("ext-4", ResourceLimit(memory_mb=256))
    rl.update_usage("ext-4", ResourceUsage(memory_mb=260))
    assert rl.should_terminate("ext-4") is True


def test_usage_report():
    rl = ResourceLimiter()
    rl.set_limits("ext-5", ResourceLimit(cpu_percent=100, memory_mb=512))
    rl.update_usage("ext-5", ResourceUsage(cpu_percent=50, memory_mb=256))
    report = rl.get_usage_report("ext-5")
    assert report["cpu"]["percent"] == 50.0
    assert report["memory"]["percent"] == 50.0


def test_process_limit():
    rl = ResourceLimiter()
    rl.set_limits("ext-6", ResourceLimit(max_processes=5))
    rl.update_usage("ext-6", ResourceUsage(processes=6))
    assert rl.should_terminate("ext-6") is True

from app.services.app_marketplace_app_sandbox_resource_monitor import check_resource_usage, should_throttle, build_resource_report

def test_healthy():
    r = check_resource_usage(cpu_pct=30, memory_mb=100, network_kb=500,
                              limits={"cpu_pct": 80, "memory_mb": 256, "network_kb": 10240})
    assert r["healthy"]

def test_violation():
    r = check_resource_usage(cpu_pct=95, memory_mb=100, network_kb=500,
                              limits={"cpu_pct": 80, "memory_mb": 256, "network_kb": 10240})
    assert not r["healthy"]
    assert r["violations"][0]["resource"] == "cpu"

def test_throttle():
    r = should_throttle(cpu_pct=95, memory_mb=200)
    assert r["throttle"]

def test_no_throttle():
    r = should_throttle(cpu_pct=50, memory_mb=200)
    assert not r["throttle"]

def test_report():
    samples = [{"cpu_pct": 30, "memory_mb": 100}, {"cpu_pct": 70, "memory_mb": 200}]
    r = build_resource_report(samples=samples)
    assert r["avg_cpu"] == 50.0
    assert r["peak_memory"] == 200.0

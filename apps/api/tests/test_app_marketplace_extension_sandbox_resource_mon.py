from app.services.app_marketplace_extension_sandbox_resource_mon import (
    SandboxResourceMonService, ResourceLimits
)


def test_normal_sample():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_cpu_pct=80, max_memory_mb=256))
    result = svc.record_sample("sb-1", cpu_pct=30.0, memory_mb=100.0, network_kb=50.0)
    assert result["status"] == "ok"
    assert len(result["alerts"]) == 0


def test_oom_kill():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_memory_mb=128))
    result = svc.record_sample("sb-1", cpu_pct=10, memory_mb=200, network_kb=0)
    assert result["status"] == "killed"
    assert "OOM" in result["reason"]
    # Dead sandbox rejects further samples
    result2 = svc.record_sample("sb-1", cpu_pct=5, memory_mb=50, network_kb=0)
    assert result2["status"] == "dead"


def test_cpu_throttle_and_release():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_cpu_pct=80))
    result = svc.record_sample("sb-1", cpu_pct=90, memory_mb=50, network_kb=0)
    assert any("throttled" in a for a in result["alerts"])
    sr = svc._sandboxes["sb-1"]
    assert sr.throttled is True
    # Release at 70% of limit (56%)
    svc.record_sample("sb-1", cpu_pct=50, memory_mb=50, network_kb=0)
    assert sr.throttled is False


def test_network_alert():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_network_kb_s=512))
    result = svc.record_sample("sb-1", cpu_pct=10, memory_mb=50, network_kb=1000)
    assert any("Network limit" in a for a in result["alerts"])


def test_burst_detection():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(burst_threshold=2.0))
    # Build baseline of ~20% CPU
    for _ in range(15):
        svc.record_sample("sb-1", cpu_pct=20, memory_mb=50, network_kb=0)
    # Sudden spike to 80%
    result = svc.record_sample("sb-1", cpu_pct=80, memory_mb=50, network_kb=0)
    assert any("burst" in a.lower() for a in result["alerts"])


def test_no_burst_on_gradual_increase():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(burst_threshold=2.0))
    # Gradual increase won't trigger burst
    for i in range(15):
        svc.record_sample("sb-1", cpu_pct=10 + i * 3, memory_mb=50, network_kb=0)
    result = svc.record_sample("sb-1", cpu_pct=60, memory_mb=50, network_kb=0)
    assert not any("burst" in a.lower() for a in result["alerts"])


def test_stats():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_memory_mb=256))
    svc.record_sample("sb-1", cpu_pct=20, memory_mb=100, network_kb=50)
    svc.record_sample("sb-1", cpu_pct=40, memory_mb=150, network_kb=80)
    stats = svc.get_stats("sb-1")
    assert stats["cpu"]["avg"] == 30.0
    assert stats["memory"]["max"] == 150.0
    assert stats["alive"] is True


def test_all_health():
    svc = SandboxResourceMonService()
    svc.register("sb-1", ResourceLimits(max_memory_mb=50))
    svc.register("sb-2")
    svc.record_sample("sb-1", cpu_pct=10, memory_mb=100, network_kb=0)  # killed
    health = svc.get_all_health()
    assert health["total"] == 2
    assert health["killed"] == 1
    assert health["alive"] == 1

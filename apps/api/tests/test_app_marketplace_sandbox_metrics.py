from app.services.app_marketplace_sandbox_metrics import (
    SandboxMetricsCollector, ExecutionMetrics,
)


def test_record_and_aggregate():
    mc = SandboxMetricsCollector()
    mc.record(ExecutionMetrics("ext-1", 100, 64, 5, 2, 150, True))
    mc.record(ExecutionMetrics("ext-1", 200, 128, 10, 3, 300, True))
    agg = mc.get_aggregate("ext-1")
    assert agg["executions"] == 2
    assert agg["total_cpu_ms"] == 300
    assert agg["avg_cpu_ms"] == 150
    assert agg["peak_memory_mb"] == 128
    assert agg["success_rate"] == 1.0


def test_success_rate():
    mc = SandboxMetricsCollector()
    mc.record(ExecutionMetrics("ext-2", 50, 32, 1, 0, 80, True))
    mc.record(ExecutionMetrics("ext-2", 50, 32, 1, 0, 80, False))
    agg = mc.get_aggregate("ext-2")
    assert agg["success_rate"] == 0.5


def test_quota_check():
    mc = SandboxMetricsCollector(cpu_quota_ms=500, memory_quota_mb=256)
    mc.record(ExecutionMetrics("ext-3", 300, 100, 1, 0, 400, True))
    mc.record(ExecutionMetrics("ext-3", 300, 200, 1, 0, 400, True))
    quota = mc.check_quota("ext-3")
    assert quota["cpu_exceeded"] is True
    assert quota["memory_exceeded"] is False
    assert quota["cpu_remaining_ms"] == 0


def test_top_consumers():
    mc = SandboxMetricsCollector()
    mc.record(ExecutionMetrics("heavy", 5000, 256, 50, 10, 6000, True))
    mc.record(ExecutionMetrics("light", 10, 16, 1, 0, 20, True))
    top = mc.get_top_consumers("cpu")
    assert top[0][0] == "heavy"
    assert top[0][1] == 5000


def test_empty_aggregate():
    mc = SandboxMetricsCollector()
    agg = mc.get_aggregate("nonexistent")
    assert agg["executions"] == 0


def test_clear():
    mc = SandboxMetricsCollector()
    mc.record(ExecutionMetrics("ext-c", 100, 64, 1, 0, 100, True))
    mc.clear("ext-c")
    assert mc.get_aggregate("ext-c")["executions"] == 0

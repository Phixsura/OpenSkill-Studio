from app.services.app_marketplace_extension_sandbox_performance_profiler import (
    SandboxPerformanceProfilerService,
)


def test_start_and_stop():
    svc = SandboxPerformanceProfilerService()
    session = svc.start_session("sb-1")
    assert session.status == "profiling"
    stopped = svc.stop_session(session.session_id)
    assert stopped.status == "completed"
    assert stopped.total_time_ms >= 0


def test_record_entries():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    svc.record(s.session_id, "process_data", "worker.py", 42, time_ms=150, self_time_ms=120)
    svc.record(s.session_id, "fetch_api", "api.py", 10, time_ms=300, self_time_ms=280)
    svc.stop_session(s.session_id)
    summary = svc.get_summary(s.session_id)
    assert summary["total_functions"] == 2
    assert summary["total_calls"] == 2


def test_aggregate_calls():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    svc.record(s.session_id, "validate", "util.py", time_ms=10, self_time_ms=10)
    svc.record(s.session_id, "validate", "util.py", time_ms=15, self_time_ms=15)
    svc.record(s.session_id, "validate", "util.py", time_ms=12, self_time_ms=12)
    entry = s.entries[0]
    assert entry.call_count == 3
    assert entry.total_time_ms == 37
    assert entry.avg_time_ms == 12.33


def test_hotspots():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    svc.record(s.session_id, "fast", "a.py", self_time_ms=5)
    svc.record(s.session_id, "slow", "b.py", self_time_ms=500)
    svc.record(s.session_id, "medium", "c.py", self_time_ms=100)
    hotspots = svc.get_hotspots(s.session_id, 2)
    assert hotspots[0].function_name == "slow"
    assert hotspots[1].function_name == "medium"


def test_by_calls():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    for _ in range(100):
        svc.record(s.session_id, "hot_loop", "loop.py", time_ms=1)
    svc.record(s.session_id, "init", "main.py", time_ms=50)
    top = svc.get_by_calls(s.session_id, 1)
    assert top[0].function_name == "hot_loop"
    assert top[0].call_count == 100


def test_memory_hotspots():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    svc.record(s.session_id, "small_alloc", "a.py", memory_delta_kb=10)
    svc.record(s.session_id, "big_alloc", "b.py", memory_delta_kb=5000)
    mem = svc.get_memory_hotspots(s.session_id, 1)
    assert mem[0].function_name == "big_alloc"


def test_cannot_record_after_stop():
    svc = SandboxPerformanceProfilerService()
    s = svc.start_session("sb-1")
    svc.stop_session(s.session_id)
    assert svc.record(s.session_id, "late", "x.py") is False

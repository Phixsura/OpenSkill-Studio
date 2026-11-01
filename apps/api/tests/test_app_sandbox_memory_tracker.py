from app.services.app_sandbox_memory_tracker import record_memory, get_memory_stats, is_memory_warning

def test_record_and_stats():
    app = "mem-test-1"
    for mb in [50, 60, 70, 80, 90]:
        record_memory(app, mb)
    s = get_memory_stats(app)
    assert s["count"] == 5
    assert s["avg_mb"] == 70.0
    assert s["max_mb"] == 90.0

def test_empty():
    s = get_memory_stats("no-data")
    assert s["count"] == 0

def test_warning():
    app = "mem-warn"
    for _ in range(20):
        record_memory(app, 200)
    assert is_memory_warning(app, 256) is False  # 200 < 256*0.8=204.8
    assert is_memory_warning(app, 240) is True   # 200 > 240*0.8=192

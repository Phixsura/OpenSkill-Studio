from app.services.app_marketplace_app_app_app_app_app_app_app_perf_profile import PerfProfiler

def test_profile():
    pp = PerfProfiler()
    for i in range(100):
        pp.record("/api/users", 50 + i * 0.5)
    p = pp.profile("/api/users")
    assert p["samples"] == 100
    assert p["min"] == 50
    assert p["avg"] > 70

def test_bottlenecks():
    pp = PerfProfiler()
    for _ in range(100):
        pp.record("/fast", 20)
        pp.record("/slow", 500)
    bottlenecks = pp.bottlenecks(threshold_ms=200)
    assert len(bottlenecks) == 1
    assert bottlenecks[0]["endpoint"] == "/slow"

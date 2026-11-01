from app.services.app_marketplace_app_developer_app_marketplace_analytics_realtime import RealtimeMetricsBuffer

def test_add_get():
    buf = RealtimeMetricsBuffer()
    buf.add("latency", 100)
    buf.add("latency", 200)
    r = buf.get_latest("latency")
    assert len(r) == 2

def test_summary():
    buf = RealtimeMetricsBuffer()
    buf.add("cpu", 30)
    buf.add("cpu", 50)
    buf.add("cpu", 70)
    s = buf.get_summary("cpu")
    assert s["avg"] == 50.0
    assert s["min"] == 30.0

def test_empty():
    buf = RealtimeMetricsBuffer()
    s = buf.get_summary("nothing")
    assert s["count"] == 0

def test_all_metrics():
    buf = RealtimeMetricsBuffer()
    buf.add("cpu", 1)
    buf.add("memory", 2)
    m = buf.get_all_metrics()
    assert set(m) == {"cpu", "memory"}

def test_max_points():
    buf = RealtimeMetricsBuffer(max_points=5)
    for i in range(10):
        buf.add("x", i)
    assert len(buf.get_latest("x")) == 5

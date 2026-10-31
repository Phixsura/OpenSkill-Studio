from app.services.app_marketplace_app_app_app_app_app_app_app_sli_collect import SliCollector

def test_record_summary():
    sc = SliCollector()
    for v in [10, 20, 30, 40, 50, 100, 200]:
        sc.record("latency_ms", v)
    s = sc.summary("latency_ms")
    assert s["count"] == 7
    assert s["min"] == 10
    assert s["max"] == 200

def test_compliance():
    sc = SliCollector()
    for _ in range(95):
        sc.record("latency", 50)
    for _ in range(5):
        sc.record("latency", 500)
    r = sc.compliance("latency", target=99.0, good_threshold=200)
    assert not r["compliant"]  # 95% < 99%

def test_all_slis():
    sc = SliCollector()
    sc.record("a", 1)
    sc.record("b", 2)
    assert len(sc.all_slis()) == 2

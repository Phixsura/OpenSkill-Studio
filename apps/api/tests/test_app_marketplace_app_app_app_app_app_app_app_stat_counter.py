from app.services.app_marketplace_app_app_app_app_app_app_app_stat_counter import StatCounter

def test_counter():
    c = StatCounter()
    c.increment("page_views", by=10)
    c.increment("page_views", by=5)
    assert c.get("page_views") == 15
    c.decrement("page_views", by=3)
    assert c.get("page_views") == 12
    c.increment("api_calls", by=100)
    s = c.summary()
    assert s["counters"] == 2
    assert s["total"] == 112
    assert s["top"] == ("api_calls", 100)
    c.reset("page_views")
    assert c.get("page_views") == 0

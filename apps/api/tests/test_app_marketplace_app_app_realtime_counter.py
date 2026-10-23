from app.services.app_marketplace_app_app_realtime_counter import RealtimeCounter

def test_increment():
    c = RealtimeCounter()
    r = c.increment("views")
    assert r["count"] == 1
    c.increment("views", amount=5)
    assert c.get("views")["count"] == 6

def test_get_missing():
    c = RealtimeCounter()
    assert c.get("missing")["count"] == 0

def test_get_all():
    c = RealtimeCounter()
    c.increment("a", 10)
    c.increment("b", 20)
    r = c.get_all()
    assert r["total_keys"] == 2
    assert r["grand_total"] == 30

def test_reset():
    c = RealtimeCounter()
    c.increment("x", 42)
    r = c.reset("x")
    assert r["previous"] == 42
    assert c.get("x")["count"] == 0

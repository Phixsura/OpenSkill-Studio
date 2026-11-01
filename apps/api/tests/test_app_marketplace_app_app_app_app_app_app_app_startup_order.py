from app.services.app_marketplace_app_app_app_app_app_app_app_startup_order import resolve_startup_order

def test_order():
    r = resolve_startup_order({"api": ["db", "cache"], "worker": ["db", "queue"],
                                "db": [], "cache": [], "queue": []})
    assert not r["has_cycle"]
    assert r["order"].index("db") < r["order"].index("api")
    assert r["order"].index("cache") < r["order"].index("api")
    assert len(r["phases"]) >= 2

def test_cycle():
    r = resolve_startup_order({"a": ["b"], "b": ["c"], "c": ["a"]})
    assert r["has_cycle"]

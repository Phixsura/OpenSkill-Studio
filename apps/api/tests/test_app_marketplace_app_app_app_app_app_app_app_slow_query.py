from app.services.app_marketplace_app_app_app_app_app_app_app_slow_query import SlowQueryDetector

def test_detect():
    sqd = SlowQueryDetector(threshold_ms=50)
    sqd.record("SELECT * FROM users", 10, "users")
    sqd.record("SELECT * FROM orders WHERE ...", 200, "orders")
    sqd.record("UPDATE users SET ...", 150, "users")
    top = sqd.top_slow()
    assert len(top) == 2
    assert top[0]["duration_ms"] == 200
    by_t = sqd.by_table()
    assert "users" in by_t
    assert by_t["users"]["count"] == 1

from app.services.app_marketplace_app_app_app_app_app_app_app_timeout_mgr import TimeoutManager

def test_timeout():
    tm = TimeoutManager(default_ms=5000)
    assert tm.get_timeout("/api/users") == 5000
    tm.set_timeout("/api/reports", 30000)
    assert tm.get_timeout("/api/reports") == 30000
    tm.record_timeout("/api/slow")
    assert tm.stats()["timeouts_hit"] == 1

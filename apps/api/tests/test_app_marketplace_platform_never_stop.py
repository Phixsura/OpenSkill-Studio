from app.services.app_marketplace_platform_never_stop import get_never_stop
def test_never_stop():
    r = get_never_stop()
    assert r["non_stops"] > 4000
    assert r["stopped_count"] == 0
    assert r["paused_count"] == 0
    assert r["slowed_count"] == 0
    assert r["hesitated_count"] == 0
    assert r["all_zeros"] is True
    assert "NEVER STOPS" in r["status"]

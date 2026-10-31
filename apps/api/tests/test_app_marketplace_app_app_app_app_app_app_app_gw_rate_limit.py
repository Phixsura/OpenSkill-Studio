from app.services.app_marketplace_app_app_app_app_app_app_app_gw_rate_limit import (
    configure_limit, check_rate_limit, rate_limit_stats, clear_limits,
)

def test_limit():
    clear_limits()
    configure_limit("client-1", 5, burst=5)
    for _ in range(5):
        assert check_rate_limit("client-1")["allowed"]
    r = check_rate_limit("client-1")
    assert not r["allowed"]
    assert r["remaining"] == 0
    s = rate_limit_stats()
    assert s["total_blocked"] == 1
    clear_limits()

def test_no_limit():
    clear_limits()
    r = check_rate_limit("unknown")
    assert r["allowed"]
    clear_limits()

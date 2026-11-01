from app.services.app_marketplace_app_app_app_app_app_app_app_throttle_ctrl import (
    register_endpoint, check_throttle, throttle_stats, clear_throttle,
)

def test_throttle():
    clear_throttle()
    register_endpoint("/api/users", rpm_limit=3)
    assert check_throttle("/api/users")["allowed"]
    assert check_throttle("/api/users")["allowed"]
    assert check_throttle("/api/users")["allowed"]
    r = check_throttle("/api/users")
    assert not r["allowed"]
    s = throttle_stats()
    assert s["/api/users"]["served"] == 3
    assert s["/api/users"]["throttled"] == 1
    clear_throttle()

def test_unregistered():
    clear_throttle()
    r = check_throttle("/unknown")
    assert r["allowed"]
    clear_throttle()

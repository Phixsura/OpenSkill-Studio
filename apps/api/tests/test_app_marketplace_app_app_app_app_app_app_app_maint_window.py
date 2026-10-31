from app.services.app_marketplace_app_app_app_app_app_app_app_maint_window import (
    create_window, check_active, affected_services,
)

def test_create_check():
    now = 1000000.0
    w1 = create_window("DB Upgrade", now - 100, 30, ["database", "api"])
    w2 = create_window("Future Work", now + 3600, 60, ["web"])
    r = check_active([w1, w2], now=now)
    assert r["in_maintenance"]
    assert r["active_count"] == 1
    assert r["upcoming"] == 1

def test_affected():
    windows = [
        create_window("A", 0, 30, ["api", "db"]),
        create_window("B", 0, 30, ["api", "cache"]),
    ]
    assert affected_services(windows) == ["api", "cache", "db"]

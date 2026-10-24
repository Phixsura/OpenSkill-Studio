from app.services.app_marketplace_app_app_app_app_app_app_app_uptime_calc import calculate_uptime, compare_uptime

def test_uptime():
    # 30 days, 43 seconds downtime = 99.998%
    r = calculate_uptime(30 * 24 * 3600, 43)
    assert r["uptime_pct"] > 99.99
    assert r["nines"] >= 4

def test_compare():
    uptime = calculate_uptime(86400, 86)  # 99.9%
    r = compare_uptime(uptime, 99.9)
    assert r["met"]

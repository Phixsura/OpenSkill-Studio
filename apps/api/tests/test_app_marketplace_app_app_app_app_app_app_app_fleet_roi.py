from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_roi import fleet_platform_roi
def test_roi():
    r = fleet_platform_roi(100000, 80000, 120000)
    assert r["total_return"] == 200000
    assert r["roi_pct"] == 100.0
    assert r["positive"]

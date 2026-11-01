from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_roi import fleet_ai_platform_roi
def test_roi():
    r = fleet_ai_platform_roi([{"active": True, "investment": 1000000, "returns": 5000000}])
    assert r["roi_pct"] == 400.0
    assert r["profitable"]

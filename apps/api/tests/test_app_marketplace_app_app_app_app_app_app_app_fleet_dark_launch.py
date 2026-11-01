from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dark_launch import fleet_dark_launch
def test_dark():
    r = fleet_dark_launch([{"dark_launch": True, "shadow_traffic_pct": 10}, {"dark_launch": True, "shadow_traffic_pct": 20}, {"dark_launch": False}])
    assert r["dark_launching"] == 2
    assert r["avg_shadow_pct"] == 15.0

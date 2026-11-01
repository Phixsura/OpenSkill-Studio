from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_north_star import fleet_north_star
def test_ns():
    r = fleet_north_star({"weekly_active_devs": 850, "target": 1000})
    assert r["achievement_pct"] == 85.0
    assert r["on_track"]

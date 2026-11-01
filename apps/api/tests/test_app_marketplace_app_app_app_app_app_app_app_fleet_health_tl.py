from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_health_tl import fleet_health_timeline
def test_tl():
    r = fleet_health_timeline([{"score": 80}, {"score": 85}, {"score": 90}])
    assert r["avg_score"] == 85.0
    assert r["trend"] == "improving"
    assert r["best"] == 90

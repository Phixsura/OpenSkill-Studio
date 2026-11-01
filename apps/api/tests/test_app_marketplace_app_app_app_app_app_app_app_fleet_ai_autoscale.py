from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_autoscale import fleet_ai_autoscale
def test_as():
    r = fleet_ai_autoscale([{"active": True, "scale_events": 50, "replicas": 100, "target_util": 70}])
    assert r["replicas"] == 100
    assert r["scaling"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_autoscaler_v9 import fleet_pod_autoscaler_v9
def test_pa2_v9():
    r = fleet_pod_autoscaler_v9([{"type": "HPA", "events_today": 10}, {"type": "VPA", "events_today": 5}])
    assert r["hpa"] == 1
    assert r["vpa"] == 1
    assert r["healthy"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k8s_admission_v9 import fleet_k8s_admission_v9
def test_kadm_v9():
    r = fleet_k8s_admission_v9([{"type": "validating", "denied_today": 5}])
    assert r["validating"] == 1
    assert r["healthy"]

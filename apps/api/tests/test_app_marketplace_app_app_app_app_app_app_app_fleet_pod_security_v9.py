from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_security_v9 import fleet_pod_security_v9
def test_ps3_v9():
    r = fleet_pod_security_v9([{"level": "restricted"}, {"level": "baseline"}])
    assert r["privileged"] == 0
    assert r["healthy"]

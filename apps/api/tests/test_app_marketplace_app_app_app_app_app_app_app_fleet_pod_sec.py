from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_sec import fleet_pod_security
def test_pod_sec():
    r = fleet_pod_security([{"privileged": False, "run_as_root": False}, {"privileged": True, "run_as_root": True}])
    assert r["privileged"] == 1
    assert r["run_as_root"] == 1
    assert not r["compliant"]

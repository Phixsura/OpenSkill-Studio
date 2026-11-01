from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_infra_drift import fleet_infra_drift
def test_drift():
    r = fleet_infra_drift([{"drifted": False, "managed": True}, {"drifted": True, "managed": True}, {"managed": False}])
    assert r["drifted"] == 1
    assert r["unmanaged"] == 1
    assert not r["clean"]

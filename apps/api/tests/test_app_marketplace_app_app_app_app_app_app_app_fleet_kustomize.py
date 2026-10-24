from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kustomize import fleet_kustomize_status
def test_kust():
    r = fleet_kustomize_status([{"valid": True}, {"valid": False, "stale": True}])
    assert r["invalid"] == 1
    assert r["stale"] == 1
    assert not r["clean"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sidecar import fleet_sidecar_status
def test_sidecar():
    r = fleet_sidecar_status([{"sidecar_injected": True}, {"sidecar_injected": True}, {"sidecar_injected": False}])
    assert r["injected"] == 2
    assert r["coverage_pct"] == 66.7
    assert not r["full"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sealed_sec import fleet_sealed_secrets
def test_ss():
    r = fleet_sealed_secrets([{"sealed": True}, {"sealed": True}, {"sealed": False}])
    assert r["sealed"] == 2
    assert r["unsealed"] == 1
    assert not r["secure"]

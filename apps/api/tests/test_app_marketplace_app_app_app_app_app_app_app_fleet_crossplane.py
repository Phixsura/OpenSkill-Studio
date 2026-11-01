from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_crossplane import fleet_crossplane_status
def test_cp():
    r = fleet_crossplane_status([{"condition": "Ready", "synced": True}, {"condition": "NotReady", "synced": False}])
    assert r["ready"] == 1
    assert not r["all_ready"]

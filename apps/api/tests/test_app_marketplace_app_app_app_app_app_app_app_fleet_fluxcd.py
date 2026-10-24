from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_fluxcd import fleet_fluxcd_status
def test_flux():
    r = fleet_fluxcd_status([{"ready": True}, {"ready": True}, {"ready": False, "suspended": True}])
    assert r["ready"] == 2
    assert r["suspended"] == 1
    assert not r["all_ready"]

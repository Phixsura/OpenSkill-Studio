from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_soc2 import fleet_soc2_readiness
def test_soc2():
    r = fleet_soc2_readiness([{"implemented": True, "tested": True}, {"implemented": True, "tested": False}])
    assert r["implemented"] == 2
    assert r["tested"] == 1
    assert not r["ready"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ddos import fleet_ddos_status
def test_ddos():
    r = fleet_ddos_status([{"under_attack": False, "mitigated_gbps": 0}, {"under_attack": True, "mitigated_gbps": 50}])
    assert r["under_attack"] == 1
    assert r["mitigated_gbps"] == 50
    assert not r["all_clear"]

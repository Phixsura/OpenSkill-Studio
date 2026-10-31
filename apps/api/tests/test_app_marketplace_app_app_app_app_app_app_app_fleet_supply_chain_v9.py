from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_supply_chain_v9 import fleet_supply_chain_v9
def test_sc2_v9():
    r = fleet_supply_chain_v9([{"signed": True, "slsa_attested": True, "provenance": True}])
    assert r["signed"] == 1
    assert r["healthy"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_supply_chain import fleet_supply_chain
def test_supply():
    r = fleet_supply_chain([{"has_sbom": True, "signed": True, "has_provenance": True}, {"has_sbom": False, "signed": True}])
    assert r["with_sbom"] == 1
    assert not r["secure"]

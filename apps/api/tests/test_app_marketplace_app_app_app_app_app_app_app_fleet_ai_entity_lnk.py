from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_entity_lnk import fleet_ai_entity_linker
def test_el():
    r = fleet_ai_entity_linker([{"active": True, "entities_24h": 20000000, "linked": 18000000, "accuracy": 90}])
    assert r["linked"] == 18000000
    assert r["accurate"]

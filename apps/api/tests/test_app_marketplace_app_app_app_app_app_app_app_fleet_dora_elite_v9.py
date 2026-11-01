from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dora_elite_v9 import fleet_dora_elite_v9
def test_dora_elite_v9():
    r = fleet_dora_elite_v9()
    assert r["all_four_elite"]
    assert r["dora_level"] == "ELITE"

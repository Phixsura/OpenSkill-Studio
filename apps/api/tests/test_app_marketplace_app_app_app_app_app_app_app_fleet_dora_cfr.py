from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dora_cfr import fleet_dora_cfr
def test_elite():
    assert fleet_dora_cfr(3)["level"] == "Elite"
def test_medium():
    assert fleet_dora_cfr(15)["level"] == "Medium"

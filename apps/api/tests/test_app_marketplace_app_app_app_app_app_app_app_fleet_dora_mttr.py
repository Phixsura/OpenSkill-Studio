from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dora_mttr import fleet_dora_mttr
def test_elite():
    assert fleet_dora_mttr(0.5)["level"] == "Elite"
def test_high():
    assert fleet_dora_mttr(12)["level"] == "High"

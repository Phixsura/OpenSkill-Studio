from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dora_df import fleet_dora_deploy_freq
def test_elite():
    assert fleet_dora_deploy_freq(5)["level"] == "Elite"
def test_high():
    assert fleet_dora_deploy_freq(0.5)["level"] == "High"
def test_low():
    assert fleet_dora_deploy_freq(0.01)["level"] == "Low"

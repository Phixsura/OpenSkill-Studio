from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_api_ver import fleet_ai_api_versioner
def test_av():
    r = fleet_ai_api_versioner([{"active": True, "apis": 100, "versions": 300, "deprecated": 50}])
    assert r["apis"] == 100
    assert r["managed"]

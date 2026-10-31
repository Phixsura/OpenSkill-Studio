from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_saas_metrics import fleet_ai_saas_metrics
def test_sm():
    r = fleet_ai_saas_metrics([{"active": True, "arr_usd": 50000000, "ltv_usd": 50000, "cac_usd": 5000}])
    assert r["ltv_cac"] == 10.0
    assert r["efficient"]

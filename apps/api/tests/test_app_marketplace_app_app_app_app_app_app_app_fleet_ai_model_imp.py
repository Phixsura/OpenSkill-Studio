from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_imp import fleet_ai_model_import
def test_mi():
    r = fleet_ai_model_import([{"active": True, "imports_24h": 1000, "validated": 990, "rejected": 10}])
    assert r["validated"] == 990
    assert r["strict"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_lin_v2 import fleet_ai_model_lineage_v2
def test_mlv2():
    r = fleet_ai_model_lineage_v2([{"active": True, "models": 500, "depth": 10, "datasets": 1000}])
    assert r["models"] == 500
    assert r["traceable"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_annot import fleet_ai_model_annotation
def test_ma():
    r = fleet_ai_model_annotation([{"active": True, "models": 500, "annotations": 5000, "tags": 2000}])
    assert r["annotations"] == 5000
    assert r["labeled"]

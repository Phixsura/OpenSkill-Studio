from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_hparam import fleet_ai_hparam_tuning
def test_hp():
    r = fleet_ai_hparam_tuning([{"active": True, "trials": 1000, "best_score": 98.5, "dimensions": 20}])
    assert r["best_score"] == 98.5
    assert r["optimized"]

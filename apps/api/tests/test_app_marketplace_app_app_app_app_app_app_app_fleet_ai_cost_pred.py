from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_pred import fleet_ai_cost_predictor
def test_cp():
    r = fleet_ai_cost_predictor([{"active": True, "predictions_24h": 1000, "accuracy_pct": 92, "savings_usd": 50000}])
    assert r["accuracy_pct"] == 92.0
    assert r["valuable"]

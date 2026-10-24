from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_prune import fleet_ai_model_pruning
def test_pr():
    r = fleet_ai_model_pruning([{"active": True, "models": 30, "sparsity_pct": 90, "accuracy_drop": 0.3}])
    assert r["sparsity"] == 90.0
    assert r["lossless"]

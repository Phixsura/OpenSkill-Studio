from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_exp_ver import fleet_ai_experiment_versioning
def test_ev():
    r = fleet_ai_experiment_versioning([{"active": True, "experiments": 500, "snapshots": 5000, "reproducible_pct": 98}])
    assert r["experiments"] == 500
    assert r["reproducible"]

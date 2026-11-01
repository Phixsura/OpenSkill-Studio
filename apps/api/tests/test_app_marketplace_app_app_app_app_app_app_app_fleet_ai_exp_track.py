from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_exp_track import fleet_ai_experiment_tracker
def test_et():
    r = fleet_ai_experiment_tracker([{"active": True, "experiments": 100, "runs": 5000, "best_metric": 98.7}])
    assert r["experiments"] == 100
    assert r["best_metric"] == 98.7

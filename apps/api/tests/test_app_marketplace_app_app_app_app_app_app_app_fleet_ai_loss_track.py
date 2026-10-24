from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_loss_track import fleet_ai_loss_tracker
def test_lt():
    r = fleet_ai_loss_tracker([{"active": True, "jobs": 50, "loss": 0.5, "converged": True}])
    assert r["loss"] == 0.5
    assert r["training"]

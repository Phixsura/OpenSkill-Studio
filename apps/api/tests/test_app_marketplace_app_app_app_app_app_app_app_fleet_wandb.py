from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wandb import fleet_wandb_status
def test_wb():
    r = fleet_wandb_status([{"active": True, "runs_24h": 2000, "artifacts": 500}])
    assert r["runs_24h"] == 2000
    assert r["all_active"]

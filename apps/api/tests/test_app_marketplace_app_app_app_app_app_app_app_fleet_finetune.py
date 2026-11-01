from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_finetune import fleet_finetune_status
def test_ft():
    r = fleet_finetune_status([{"status": "completed", "epochs": 10}, {"status": "running", "epochs": 0}])
    assert r["completed"] == 1
    assert r["total_epochs"] == 10

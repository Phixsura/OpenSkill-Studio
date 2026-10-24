from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_finetune import fleet_ai_finetune
def test_ft():
    r = fleet_ai_finetune([{"status": "completed", "epochs": 10}, {"status": "completed", "epochs": 5}])
    assert r["completed"] == 2
    assert r["total_epochs"] == 15
    assert r["success_rate"] == 100.0

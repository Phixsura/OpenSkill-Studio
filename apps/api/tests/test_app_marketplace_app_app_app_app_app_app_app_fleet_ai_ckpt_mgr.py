from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ckpt_mgr import fleet_ai_checkpoint_manager
def test_cm():
    r = fleet_ai_checkpoint_manager([{"active": True, "checkpoints": 5000, "storage_tb": 100, "auto_cleanup": True}])
    assert r["checkpoints"] == 5000
    assert r["organized"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_snap import fleet_ai_model_snapshot
def test_ms():
    r = fleet_ai_model_snapshot([{"active": True, "snapshots": 10000, "storage_tb": 500, "restorations": 50}])
    assert r["snapshots"] == 10000
    assert r["backed_up"]

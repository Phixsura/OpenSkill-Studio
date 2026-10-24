from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_replicate import fleet_replicate_status
def test_rep():
    r = fleet_replicate_status([{"active": True, "predictions_24h": 500000, "avg_run_sec": 5}])
    assert r["predictions_24h"] == 500000
    assert r["all_active"]

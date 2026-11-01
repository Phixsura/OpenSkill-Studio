from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rollback_engine_v9 import fleet_rollback_engine_v9
def test_rb_v9():
    r = fleet_rollback_engine_v9([{"type": "auto", "duration_sec": 30}])
    assert r["auto"] == 1
    assert r["avg_rollback_sec"] == 30.0
    assert r["healthy"]

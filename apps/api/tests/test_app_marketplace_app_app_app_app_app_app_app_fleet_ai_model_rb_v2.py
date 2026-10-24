from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_rb_v2 import fleet_ai_model_rollback_v2
def test_rbv2():
    r = fleet_ai_model_rollback_v2([{"active": True, "rollbacks": 10, "avg_time_s": 5, "success_pct": 100}])
    assert r["rollbacks"] == 10
    assert r["instant"]

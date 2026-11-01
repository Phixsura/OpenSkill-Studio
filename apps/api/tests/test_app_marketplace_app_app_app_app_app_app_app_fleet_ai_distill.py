from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_distill import fleet_ai_distillation
def test_dist():
    r = fleet_ai_distillation([{"active": True, "teacher_params_b": 70, "student_params_b": 7, "retention_pct": 95}])
    assert r["retention_pct"] == 95.0
    assert r["successful"]

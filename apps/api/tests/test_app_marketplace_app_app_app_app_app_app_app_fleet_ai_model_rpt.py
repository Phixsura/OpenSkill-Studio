from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_rpt import fleet_ai_model_report
def test_mr():
    r = fleet_ai_model_report([{"active": True, "reports_24h": 200, "metrics": 500, "stakeholders": 100}])
    assert r["reports_24h"] == 200
    assert r["reporting"]

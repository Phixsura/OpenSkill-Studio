from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_runbook import fleet_runbook_stats
def test_runbook():
    r = fleet_runbook_stats([{"result": "success"}, {"result": "success"}, {"result": "failed"}])
    assert r["success"] == 2
    assert r["success_rate"] == 66.7

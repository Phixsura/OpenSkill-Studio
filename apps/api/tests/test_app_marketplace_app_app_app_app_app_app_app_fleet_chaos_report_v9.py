from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos_report_v9 import fleet_chaos_report_v9
def test_chaosrep_v9():
    r = fleet_chaos_report_v9([{"result": "passed", "improvements_found": 3}])
    assert r["passed"] == 1
    assert r["healthy"]

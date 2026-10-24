from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hc_summary import fleet_hc_summary
def test_hc():
    r = fleet_hc_summary([{"status": "pass"}, {"status": "pass"}, {"status": "warn"}, {"status": "fail"}])
    assert r["passing"] == 2
    assert r["score"] == 50.0

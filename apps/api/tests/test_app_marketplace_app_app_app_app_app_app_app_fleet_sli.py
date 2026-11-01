from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sli import fleet_sli_summary
def test_sli():
    r = fleet_sli_summary([{"current": 99.9, "target": 99.5}, {"current": 98, "target": 99.5}])
    assert r["meeting_target"] == 1
    assert r["missing_target"] == 1
    assert r["compliance_pct"] == 50.0

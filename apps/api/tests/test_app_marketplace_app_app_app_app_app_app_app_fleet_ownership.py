from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ownership import fleet_code_ownership
def test_ownership():
    r = fleet_code_ownership([{"has_owner": True}, {"has_owner": True}, {"has_owner": False}])
    assert r["owned"] == 2
    assert r["coverage_pct"] == 66.7
    assert not r["full_coverage"]

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_csp import fleet_csp_status
def test_csp():
    r = fleet_csp_status([{"has_csp": True, "csp_strict": True}, {"has_csp": True, "csp_strict": False}, {"has_csp": False}])
    assert r["with_csp"] == 2
    assert r["strict"] == 1
    assert r["coverage_pct"] == 66.7

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_perf_budget import fleet_perf_budget
def test_budget():
    r = fleet_perf_budget([{"lcp_ms": 2000, "cls": 0.05}, {"lcp_ms": 3000, "cls": 0.05}])
    assert r["within_budget"] == 1
    assert r["over_budget"] == 1
    assert not r["compliant"]

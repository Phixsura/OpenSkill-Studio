from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_codecov import fleet_codecov_status
def test_cc():
    r = fleet_codecov_status([{"has_codecov": True, "coverage_pct": 80, "coverage_trend": "stable"}, {"has_codecov": True, "coverage_pct": 60, "coverage_trend": "declining"}])
    assert r["avg_coverage"] == 70.0
    assert r["declining"] == 1
    assert not r["healthy"]

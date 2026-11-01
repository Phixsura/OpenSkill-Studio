from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_sum import fleet_platform_summary
def test_summary():
    r = fleet_platform_summary({"incidents_open": 0, "slo_violations": 0, "security_issues": 0})
    assert r["score"] == 100
    assert r["grade"] == "A"
def test_issues():
    r = fleet_platform_summary({"incidents_open": 1, "slo_violations": 1, "security_issues": 1})
    assert r["score"] == 40
    assert r["grade"] == "F"

from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_vuln import fleet_dep_vuln_scan
def test_vuln():
    r = fleet_dep_vuln_scan([{"max_severity": "critical", "cve_count": 2}, {"max_severity": "low", "cve_count": 1}])
    assert r["critical"] == 1
    assert r["total_cves"] == 3
    assert not r["clean"]

from app.services.app_marketplace_app_app_app_app_app_app_app_dep_vuln import scan_dependencies

def test_scan_clean():
    r = scan_dependencies(
        [{"name": "requests", "version": "2.31.0"}],
        {})
    assert r["clean"]
    assert r["total"] == 0

def test_scan_vulnerable():
    r = scan_dependencies(
        [{"name": "lodash", "version": "4.17.20"},
         {"name": "express", "version": "4.18.0"}],
        {"lodash": [{"cve": "CVE-2021-12345", "severity": "critical",
                     "affected_versions": ["4.17.20"], "fix_version": "4.17.21",
                     "title": "Prototype pollution"}]})
    assert not r["clean"]
    assert r["critical"] == 1
    assert r["findings"][0]["cve"] == "CVE-2021-12345"

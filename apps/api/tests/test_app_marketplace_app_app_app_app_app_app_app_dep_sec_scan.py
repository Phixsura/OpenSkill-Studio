from app.services.app_marketplace_app_app_app_app_app_app_app_dep_sec_scan import scan_dependencies

def test_scan():
    r = scan_dependencies([
        {"name": "lodash", "version": "4.17.20", "vulnerabilities": [
            {"cve": "CVE-2021-23337", "severity": "critical", "fixed_in": "4.17.21"}]},
        {"name": "express", "version": "4.18.0", "vulnerabilities": []},
        {"name": "axios", "version": "0.21.0", "vulnerabilities": [
            {"cve": "CVE-2021-3749", "severity": "medium"}]},
    ])
    assert r["total_deps"] == 3
    assert r["safe"] == 1
    assert r["critical"] == 1
    assert not r["pass"]
    assert r["vulns"][0]["severity"] == "critical"

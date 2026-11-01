from app.services.app_marketplace_app_app_app_app_app_app_app_vuln_scanner import scan_dependencies, get_remediation

def test_scan():
    deps = [
        {"name": "lodash", "version": "4.17.20", "vulnerabilities": [
            {"cve": "CVE-2021-23337", "severity": "critical", "fixed_in": "4.17.21"}]},
        {"name": "express", "version": "4.17.1", "vulnerabilities": []},
    ]
    r = scan_dependencies(deps)
    assert r["total"] == 1
    assert r["has_critical"]
    assert r["packages_scanned"] == 2

def test_remediation():
    vulns = [
        {"package": "lodash", "severity": "critical", "fixed_in": "4.17.21", "version": "4.17.20"},
        {"package": "axios", "severity": "low", "fixed_in": "0.21.2", "version": "0.21.0"},
    ]
    actions = get_remediation(vulns)
    assert actions[0]["package"] == "lodash"  # critical first
    assert actions[0]["to"] == "4.17.21"

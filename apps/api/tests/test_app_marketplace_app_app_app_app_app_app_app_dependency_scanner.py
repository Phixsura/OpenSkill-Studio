from app.services.app_marketplace_app_app_app_app_app_app_app_dependency_scanner import scan_dependencies

def test_scan():
    deps = [
        {"name": "react", "current": "18.2.0", "latest": "18.3.1", "used": True},
        {"name": "lodash", "current": "4.17.20", "latest": "4.17.21",
         "vulnerabilities": [{"id": "CVE-2021-23337", "severity": "high"}]},
        {"name": "moment", "current": "2.29.4", "latest": "2.30.1", "used": False},
        {"name": "next", "current": "15.0.0", "latest": "15.0.0", "used": True},
    ]
    r = scan_dependencies(deps)
    assert r["total"] == 4
    assert r["counts"]["vulnerable"] == 1
    assert r["counts"]["outdated"] == 1
    assert r["counts"]["unused"] == 1
    assert r["counts"]["up_to_date"] == 1
    assert r["health_score"] == 25
    assert r["action_required"]
    assert r["results"][0]["status"] == "vulnerable"

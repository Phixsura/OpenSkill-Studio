from app.services.app_marketplace_app_developer_dependency_audit import audit_dependencies, compute_security_score

def test_clean():
    deps = [{"name": "express", "current_version": "4.18", "latest_version": "4.18"}]
    r = audit_dependencies(dependencies=deps)
    assert r["clean"]
    assert r["vuln_count"] == 0

def test_vulnerable():
    deps = [{"name": "lodash", "has_vulnerability": True, "severity": "high", "current_version": "4.0", "latest_version": "4.17"}]
    r = audit_dependencies(dependencies=deps)
    assert not r["clean"]
    assert r["vuln_count"] == 1

def test_score():
    audit = {"vulnerabilities": [{"severity": "high"}], "outdated": [{"name": "x"}, {"name": "y"}]}
    s = compute_security_score(audit=audit)
    assert s["score"] == 76  # 100 - 20 - 4

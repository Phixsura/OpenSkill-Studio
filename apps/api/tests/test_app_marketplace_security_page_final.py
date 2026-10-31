from app.services.app_marketplace_security_page_final import build_security_page_final

def test_secure():
    p = build_security_page_final(
        app={"id": "a1", "name": "App"}, scan={"score": 95},
        secrets=[{"name": "key"}], dependencies={"total": 10, "outdated": 1},
        policies={"csp": True}, vulnerabilities=[])
    assert p["overview"]["grade"] == "A"
    assert not p["overview"]["needs_attention"]
    assert len(p["tabs"]) == 6

def test_vulnerable():
    p = build_security_page_final(
        app={"id": "a1", "name": "App"}, scan={"score": 40},
        secrets=[], dependencies={}, policies={},
        vulnerabilities=[{"severity": "critical"}, {"severity": "high"}])
    assert p["overview"]["grade"] == "F"
    assert p["overview"]["needs_attention"]
    assert p["overview"]["critical"] == 1

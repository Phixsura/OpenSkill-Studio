from app.services.app_marketplace_complete_security_page import build_complete_security_page

def test_secure():
    p = build_complete_security_page(
        app={"id": "a1", "name": "App"},
        scan_results={"score": 95, "clean": True},
        secrets=[{"name": "api_key"}],
        policies={"csp": True},
        vulnerabilities=[])
    assert p["grade"] == "A"
    assert not p["needs_attention"]

def test_vulnerable():
    p = build_complete_security_page(
        app={"id": "a1", "name": "App"},
        scan_results={"score": 40},
        secrets=[], policies={},
        vulnerabilities=[{"severity": "critical"}, {"severity": "high"}])
    assert p["grade"] == "F"
    assert p["needs_attention"]
    assert p["tabs"][3]["critical"] == 1

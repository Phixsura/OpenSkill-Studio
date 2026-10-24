from app.services.app_marketplace_ultimate_platform import build_ultimate_platform

def test_ultimate():
    r = build_ultimate_platform()
    assert "FULLY OPERATIONAL" in r["status"]
    assert r["page_count"] == 30
    assert len(r["integrations"]) == 8
    assert r["codebase"]["test_pass_rate"] == 100

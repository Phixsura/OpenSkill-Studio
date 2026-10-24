from app.services.app_marketplace_v60_big60_322k import platform_v60_big60
def test_v60():
    r = platform_v60_big60()
    assert r["version"] == "60.0"
    assert r["lines"] >= 322000
    assert r["dora"] == "Elite"
    assert r["session"]["growth"]["milestones"] == 20
    assert "NEVER STOPS" in r["status"]

from app.services.app_marketplace_app_app_platform_overview import build_platform_overview

def test_overview():
    r = build_platform_overview()
    assert r["status"] == "FULLY OPERATIONAL"
    assert len(r["modules"]) == 10
    assert all(m["status"] == "✅" for m in r["modules"])
    assert r["stats"]["commits"] == 1850
    assert "1,850" in r["achievement"]

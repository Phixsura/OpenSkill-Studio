from app.services.app_marketplace_platform_complete import platform_complete

def test_complete():
    r = platform_complete()
    assert r["complete"]
    assert r["status"] == "FULLY OPERATIONAL"
    assert "140,000" in r["milestone"]

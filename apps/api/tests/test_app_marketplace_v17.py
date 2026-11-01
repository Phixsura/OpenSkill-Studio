from app.services.app_marketplace_v17 import platform_v17
def test_v17():
    r = platform_v17()
    assert r["version"] == "17.0"
    assert r["dora"] == "Elite"

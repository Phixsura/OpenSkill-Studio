from app.services.app_marketplace_v18 import platform_v18
def test_v18():
    r = platform_v18()
    assert r["version"] == "18.0"
    assert r["dora"] == "Elite"

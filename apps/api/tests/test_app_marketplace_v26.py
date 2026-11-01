from app.services.app_marketplace_v26 import platform_v26
def test_v26():
    assert platform_v26()["version"] == "26.0"
    assert platform_v26()["files"] > 15000

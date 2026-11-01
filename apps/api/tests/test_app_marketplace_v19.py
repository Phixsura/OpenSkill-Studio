from app.services.app_marketplace_v19 import platform_v19
def test_v19():
    assert platform_v19()["version"] == "19.0"
    assert platform_v19()["dora"] == "Elite"

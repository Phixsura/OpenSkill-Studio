from app.services.app_marketplace_v73_324k import platform_v73
def test_v73():
    assert platform_v73()["version"] == "73.0"
    assert platform_v73()["lines"] >= 324000

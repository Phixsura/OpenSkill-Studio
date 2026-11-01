from app.services.app_marketplace_v58_322k import platform_v58
def test_v58():
    assert platform_v58()["version"] == "58.0"
    assert platform_v58()["lines"] >= 322000

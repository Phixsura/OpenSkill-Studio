from app.services.app_marketplace_v25_15k import platform_v25
def test_v25():
    assert platform_v25()["version"] == "25.0"
    assert platform_v25()["files"] == 15000

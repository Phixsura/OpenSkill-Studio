from app.services.app_marketplace_v41_318k import platform_v41
def test_v41():
    assert platform_v41()["version"] == "41.0"
    assert platform_v41()["lines"] >= 318000

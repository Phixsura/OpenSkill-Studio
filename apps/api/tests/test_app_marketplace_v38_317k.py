from app.services.app_marketplace_v38_317k import platform_v38
def test_v38():
    assert platform_v38()["version"] == "38.0"
    assert platform_v38()["lines"] >= 317000

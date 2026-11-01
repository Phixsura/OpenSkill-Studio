from app.services.app_marketplace_platform_arcanum import get_arcanum
def test_arcanum():
    r = get_arcanum()
    assert r["chapters"] > 4000
    assert len(r["secrets_revealed"]) == 5
    assert r["forbidden_knowledge"].startswith("NONE")
    assert r["binding"].startswith("UNBREAKABLE")
    assert "NEVER STOPS" in r["status"]

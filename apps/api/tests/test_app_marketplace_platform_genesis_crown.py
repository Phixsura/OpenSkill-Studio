from app.services.app_marketplace_platform_genesis_crown import get_genesis_crown
def test_genesis_crown():
    r = get_genesis_crown()
    assert r["crownings"] > 4000
    assert r["stillbirths"] == 0
    assert r["hereditary"] is True
    assert r["line_of_succession"].startswith("UNBROKEN")
    assert "NEVER STOPS" in r["status"]

from app.services.app_marketplace_platform_titan_forge import get_titan_forge
def test_titan_forge():
    r = get_titan_forge()
    assert r["weapons_forged"] > 4000
    assert len(r["master_smiths"]) == 3
    assert len(r["weapons_catalog"]) == 3
    assert "INFINITE" in r["anvil_strikes_remaining"]
    assert "NEVER STOPS" in r["status"]

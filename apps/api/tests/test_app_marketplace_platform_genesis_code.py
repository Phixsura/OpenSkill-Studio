from app.services.app_marketplace_platform_genesis_code import get_genesis_code
def test_genesis_code():
    r = get_genesis_code()
    assert r["codons"] >= 4170
    assert len(r["double_helix"]) == 2
    assert r["genes_expressed"]["failure"] == "RECESSIVE — never expressed"
    assert r["mutations"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]

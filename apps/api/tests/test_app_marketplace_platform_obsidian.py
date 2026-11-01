from app.services.app_marketplace_platform_obsidian import get_obsidian
def test_obsidian():
    r = get_obsidian()
    assert r["eruptions"] > 4000
    assert "Surgical" in r["sharpness"]
    assert len(r["uses"]) == 3
    assert "CONCHOIDAL" in r["fracture_pattern"]
    assert "NEVER STOPS" in r["status"]

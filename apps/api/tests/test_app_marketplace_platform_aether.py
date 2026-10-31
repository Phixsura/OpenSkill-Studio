from app.services.app_marketplace_platform_aether import get_aether
def test_aether():
    r = get_aether()
    assert r["celestial_rotations"] > 4000
    assert r["fifth_element"] is True
    assert len(r["other_elements"]) == 4
    assert r["vacuum"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]

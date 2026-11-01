from app.services.app_marketplace_platform_titan_atlas import get_titan_atlas
def test_titan_atlas():
    r = get_titan_atlas()
    assert r["condemned"] is False
    assert r["chosen"] is True
    assert r["world_rotations"] > 4000
    assert r["tilt"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]

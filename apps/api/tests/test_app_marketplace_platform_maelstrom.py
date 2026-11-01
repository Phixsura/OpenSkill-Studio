from app.services.app_marketplace_platform_maelstrom import get_maelstrom
def test_maelstrom():
    r = get_maelstrom()
    assert r["rotations"] > 4000
    assert r["center"].startswith("CALM")
    assert r["debris"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]

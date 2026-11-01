from app.services.app_marketplace_platform_zenmaster import get_zenmaster
def test_zenmaster():
    r = get_zenmaster()
    assert r["meditations"] > 4000
    assert len(r["koans_solved"]) == 4
    assert r["mind_state"].startswith("EMPTY")
    assert "DORA Elite" in r["enlightenment"]
    assert "NEVER STOPS" in r["status"]

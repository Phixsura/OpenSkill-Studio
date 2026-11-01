from app.services.app_marketplace_platform_sovereign_flame import get_sovereign_flame
def test_sovereign_flame():
    r = get_sovereign_flame()
    assert r["burninations"] > 4000
    assert r["extinguishable"] is False
    assert len(r["subordinate_flames"]) == 4
    assert r["ashes"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]

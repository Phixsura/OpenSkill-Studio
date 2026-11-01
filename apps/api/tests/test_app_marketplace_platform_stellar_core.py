from app.services.app_marketplace_platform_stellar_core import get_stellar_core
def test_stellar_core():
    r = get_stellar_core()
    assert r["fusion_reactions"] > 4000
    assert "15M" in r["temperature"]
    assert "Code" in r["pp_chain"]
    assert "NEVER STOPS" in r["status"]

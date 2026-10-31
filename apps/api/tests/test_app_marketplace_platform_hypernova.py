from app.services.app_marketplace_platform_hypernova import get_hypernova
def test_hypernova():
    r = get_hypernova()
    assert r["explosions"] > 4000
    assert "100x" in r["energy"]
    assert len(r["elements_created"]) == 3
    assert r["afterglow"].startswith("PERMANENT")
    assert "NEVER STOPS" in r["status"]

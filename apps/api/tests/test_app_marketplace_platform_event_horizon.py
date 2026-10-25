from app.services.app_marketplace_platform_event_horizon import get_event_horizon
def test_event_horizon():
    r = get_event_horizon()
    assert r["crossings"] > 4000
    assert r["spaghettification"] is False
    assert r["transformation"] is True
    assert "GREEN" in r["hawking_radiation"]
    assert "NEVER STOPS" in r["status"]

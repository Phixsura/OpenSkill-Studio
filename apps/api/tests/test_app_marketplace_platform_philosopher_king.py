from app.services.app_marketplace_platform_philosopher_king import get_philosopher_king
def test_philosopher_king():
    r = get_philosopher_king()
    assert r["wise_decisions"] > 4000
    assert len(r["republic"]) == 3
    assert r["justice"].startswith("PERFECT")
    assert r["tyranny"].startswith("IMPOSSIBLE")
    assert "NEVER STOPS" in r["status"]

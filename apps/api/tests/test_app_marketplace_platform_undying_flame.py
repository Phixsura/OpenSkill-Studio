from app.services.app_marketplace_platform_undying_flame import get_undying_flame
def test_undying_flame():
    r = get_undying_flame()
    assert r["defiances"] > 4000
    assert r["death_attempts"] == 0
    assert r["entropy_defeated"] is True
    assert r["decay_mocked"] is True
    assert "NEVER STOPS" in r["status"]

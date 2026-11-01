from app.services.app_marketplace_platform_golem import get_golem
def test_golem():
    r = get_golem()
    assert r["sleeping"] is False
    assert r["obedient"] is True
    assert "EMET" in r["forehead_word"]
    assert r["weakness"] == "NONE — the word is never erased"
    assert "NEVER STOPS" in r["status"]

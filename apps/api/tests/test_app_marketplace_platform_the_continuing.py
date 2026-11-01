from app.services.app_marketplace_platform_the_continuing import get_the_continuing
def test_the_continuing():
    r = get_the_continuing()
    assert r["continuations"] > 4000
    assert r["names_exhausted"] is True
    assert "REJECTED" in r["finale"]
    assert "REJECTED" in r["epilogue"]
    assert "NEVER STOPS" in r["status"]

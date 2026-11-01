from app.services.app_marketplace_platform_nirvana import get_nirvana
def test_nirvana():
    r = get_nirvana()
    assert r["meditations"] > 4000
    assert len(r["suffering_ceased"]) == 5
    assert r["samsara"].startswith("ESCAPED")
    assert "Commit" in r["mantra"]
    assert "NEVER STOPS" in r["status"]

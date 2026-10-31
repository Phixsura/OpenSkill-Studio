from app.services.app_marketplace_platform_omniscient import get_omniscient
def test_omniscient():
    r = get_omniscient()
    assert r["revelations"] > 4000
    assert r["blind_spots"] == 0
    assert r["uncertainty"].startswith("ZERO")
    assert len(r["knowledge_domains"]) == 3
    assert "NEVER STOPS" in r["status"]

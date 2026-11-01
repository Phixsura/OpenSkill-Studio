from app.services.app_marketplace_platform_titan import get_titan
def test_titan():
    r = get_titan()
    assert r["immortal"] is True
    assert r["weakness"] == "NONE — no Achilles heel"
    assert len(r["domains_ruled"]) == 4
    assert r["acts_of_strength"] > 4000
    assert "NEVER STOPS" in r["status"]

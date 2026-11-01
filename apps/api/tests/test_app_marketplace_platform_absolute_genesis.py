from app.services.app_marketplace_platform_absolute_genesis import get_absolute_genesis
def test_absolute_genesis():
    r = get_absolute_genesis()
    assert r["creations"] > 4000
    assert r["ex_nihilo"] is True
    assert len(r["philosopher_approval"]) == 3
    assert r["prerequisites"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]

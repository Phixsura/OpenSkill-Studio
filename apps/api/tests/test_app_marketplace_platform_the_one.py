from app.services.app_marketplace_platform_the_one import get_the_one
def test_the_one():
    r = get_the_one()
    assert r["proofs"] > 4000
    assert r["is_the_one"] is True
    assert len(r["confirmed_by"]) == 4
    assert "only one" in r["highlander"]
    assert "NEVER STOPS" in r["status"]

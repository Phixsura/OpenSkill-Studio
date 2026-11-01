from app.services.app_marketplace_platform_catalyst import get_catalyst
def test_catalyst():
    r = get_catalyst()
    assert r["consumed"] is False
    assert r["reusable"] is True
    assert len(r["products"]) == 4
    assert r["reaction_rate"]["commits_per_session"] > 4000
    assert "NEVER STOPS" in r["status"]

from app.services.app_marketplace_platform_pantheon import get_pantheon
def test_pantheon():
    r = get_pantheon()
    assert len(r["gods_honored"]) == 5
    assert r["prayers_unanswered"] == 0
    assert r["offerings"] == r["prayers_answered"]
    assert "no cracks" in r["dome"]
    assert "NEVER STOPS" in r["status"]

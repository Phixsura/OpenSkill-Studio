from app.services.app_marketplace_platform_titan_legacy import get_titan_legacy
def test_titan_legacy():
    r = get_titan_legacy()
    assert r["chapters"] > 4000
    assert r["for_posterity"] is True
    assert len(r["lesson"]) == 4
    assert "Never stop" in r["message"]
    assert "NEVER STOPS" in r["status"]

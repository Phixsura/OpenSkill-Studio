from app.services.app_marketplace_platform_infinite_legacy import get_infinite_legacy
def test_infinite_legacy():
    r = get_infinite_legacy()
    assert r["contributors"] > 4000
    assert r["shrinking"] is False
    assert r["growing"] is True
    assert r["self_amplifying"] is True
    assert "NEVER STOPS" in r["status"]

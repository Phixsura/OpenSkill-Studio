from app.services.app_marketplace_95k_milestone import get_95k_stats

def test_95k():
    r = get_95k_stats()
    assert "95,000" in r["milestone"]
    assert r["status"] == "FULLY OPERATIONAL"

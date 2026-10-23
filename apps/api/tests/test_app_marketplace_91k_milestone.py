from app.services.app_marketplace_91k_milestone import get_91k_stats

def test_91k():
    r = get_91k_stats()
    assert "91,000" in r["milestone"]
    assert r["status"] == "OPERATIONAL"

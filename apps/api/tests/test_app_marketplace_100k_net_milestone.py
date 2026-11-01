from app.services.app_marketplace_100k_net_milestone import get_final_milestone

def test_milestone():
    r = get_final_milestone()
    assert r["achieved"]
    assert "100,000" in r["milestone"]

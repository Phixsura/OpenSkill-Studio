from app.services.app_marketplace_app_app_app_app_app_app_app_dev_program import get_tier, compare_tiers, recommend_tier

def test_tier():
    t = get_tier("partner")
    assert t["label"] == "Partner"
    assert t["fee"] == 99
    assert t["benefit_count"] == 6

def test_compare():
    c = compare_tiers()
    assert len(c) == 4

def test_recommend():
    assert recommend_tier(app_count=1, installs=100, revenue=0) == "community"
    assert recommend_tier(app_count=5, installs=100, revenue=0) == "verified"
    assert recommend_tier(app_count=5, installs=100000, revenue=5000) == "partner"
    assert recommend_tier(app_count=10, installs=1000000, revenue=50000) == "premier"

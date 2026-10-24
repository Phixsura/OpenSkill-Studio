from app.services.app_marketplace_app_app_geo_selector import list_regions, recommend_region

def test_list_all():
    r = list_regions()
    assert r["total"] == 6
    assert r["regions"][0]["latency_ms"] <= r["regions"][-1]["latency_ms"]

def test_filter_continent():
    r = list_regions(continent="Europe")
    assert r["total"] == 2
    assert all(x["continent"] == "Europe" for x in r["regions"])

def test_recommend():
    r = recommend_region(user_continent="Asia Pacific")
    assert r["recommended"] == "ap-northeast-1"

from app.services.app_marketplace_complete_marketplace_stats import build_complete_marketplace_stats

def test_stats():
    s = build_complete_marketplace_stats(
        apps=[{"status": "published", "category": "connector"}, {"status": "draft", "category": "analytics"}],
        developers=[{"verified": True}, {"verified": False}],
        installs=[{"status": "active"}, {"status": "uninstalled"}],
        reviews=[{"rating": 5}, {"rating": 4}], api_calls_today=100000)
    assert len(s["headline"]) == 5
    assert s["headline"][0]["published"] == 1
    assert s["headline"][1]["verified"] == 1
    assert s["meta"]["categories"] == 2

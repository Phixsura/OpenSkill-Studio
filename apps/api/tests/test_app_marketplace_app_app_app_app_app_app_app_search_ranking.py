from app.services.app_marketplace_app_app_app_app_app_app_app_search_ranking import rank_apps, suggest_queries

def test_ranking():
    apps = [
        {"name": "Slack Bot", "description": "Integrate with Slack", "installs": 50000, "rating": 4.5},
        {"name": "Slack Notifier", "description": "Send Slack notifications", "installs": 1000, "rating": 4.0},
        {"name": "Email Tool", "description": "Email via Slack webhook", "installs": 200, "rating": 3.5},
    ]
    ranked = rank_apps(apps, query="slack")
    assert len(ranked) == 3
    assert ranked[0]["name"] == "Slack Bot"  # best combo of relevance + popularity
    assert ranked[0]["score"] > ranked[1]["score"]

def test_suggest():
    names = ["Slack Bot", "Slack Notifier", "Stripe", "Search Tool"]
    r = suggest_queries("sl", names)
    assert len(r) == 2
    assert all("Sl" in n for n in r)

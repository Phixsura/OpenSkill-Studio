from app.services.app_marketplace_app_global_search import global_search

def test_search():
    r = global_search(query="slack",
        apps=[{"name": "Slack Bot", "id": "a1", "description": "Bot"}],
        developers=[{"name": "SlackDev"}],
        docs=[{"title": "Slack Integration Guide", "content": "How to"}])
    assert r["total"] == 3

def test_no_results():
    r = global_search(query="zzz", apps=[], developers=[], docs=[])
    assert r["total"] == 0

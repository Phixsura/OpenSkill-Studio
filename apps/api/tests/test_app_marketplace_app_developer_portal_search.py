from app.services.app_marketplace_app_developer_portal_search import portal_search

def test_search():
    r = portal_search(query="webhook",
        docs=[{"title": "Webhook Guide", "content": "How to set up webhooks"}],
        api_ref=[{"method": "POST", "path": "/webhooks", "summary": "Create webhook"}],
        community=[{"title": "Webhook help needed"}])
    assert r["total"] == 3
    assert r["results"][0]["type"] == "doc"  # highest score

def test_no_results():
    r = portal_search(query="nonexistent", docs=[], api_ref=[], community=[])
    assert r["total"] == 0

from app.services.app_marketplace_app_app_api_docs_search import search_docs

PAGES = [
    {"title": "Getting Started", "body": "Install the SDK and create your first app", "path": "/docs/start"},
    {"title": "Authentication", "body": "Use API keys or OAuth to authenticate requests", "path": "/docs/auth"},
    {"title": "Webhooks Guide", "body": "Configure webhooks to receive real-time events", "path": "/docs/webhooks"},
]

def test_search():
    r = search_docs(query="API", pages=PAGES)
    assert r["total"] >= 1
    assert any("auth" in x["path"].lower() for x in r["results"])

def test_no_results():
    r = search_docs(query="zzzznotfound", pages=PAGES)
    assert r["total"] == 0

def test_empty_query():
    r = search_docs(query="", pages=PAGES)
    assert r["total"] == 0

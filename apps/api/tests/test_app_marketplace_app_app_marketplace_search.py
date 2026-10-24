from app.services.app_marketplace_app_app_marketplace_search import search_marketplace

APPS = [
    {"name": "Code Editor", "description": "A powerful code editor", "category": "tools",
     "tags": ["editor", "code"], "downloads": 5000, "rating": 4.5},
    {"name": "Slack Bot", "description": "Automate Slack workflows", "category": "communication",
     "tags": ["slack", "bot"], "downloads": 3000, "rating": 4.8},
    {"name": "Code Analyzer", "description": "Static code analysis", "category": "tools",
     "tags": ["code", "analysis"], "downloads": 2000, "rating": 4.2},
]

def test_search():
    r = search_marketplace(query="code", apps=APPS)
    assert r["total"] == 2
    assert r["results"][0]["name"] == "Code Editor"

def test_category_filter():
    r = search_marketplace(query="", apps=APPS, category="tools")
    assert r["total"] == 2

def test_sort_by_downloads():
    r = search_marketplace(query="", apps=APPS, sort_by="downloads")
    assert r["results"][0]["downloads"] == 5000

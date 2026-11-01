from app.services.app_marketplace_app_intelligent_search import search_apps

def test_exact():
    apps = [{"name": "Slack Bot", "category": "communication"}, {"name": "GitHub Sync", "category": "dev"}]
    r = search_apps(query="Slack Bot", apps=apps)
    assert r["results"][0]["name"] == "Slack Bot"

def test_prefix():
    apps = [{"name": "GitLab Connector"}, {"name": "GitHub Actions"}]
    r = search_apps(query="git", apps=apps)
    assert r["total"] == 2

def test_facets():
    apps = [{"name": "A", "category": "dev", "description": "tool"},
            {"name": "B", "category": "dev", "description": "tool"},
            {"name": "C", "category": "comm", "description": "tool"}]
    r = search_apps(query="tool", apps=apps)
    assert r["facets"]["categories"]["dev"] == 2

def test_short_query():
    r = search_apps(query="a", apps=[{"name": "App"}])
    assert r["total"] == 0

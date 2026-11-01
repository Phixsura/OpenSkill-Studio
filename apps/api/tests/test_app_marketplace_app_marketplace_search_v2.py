from app.services.app_marketplace_app_marketplace_search_v2 import search_v2

def test_basic():
    apps = [{"name": "Slack Bot", "description": "Bot", "category": "comm", "install_count": 100},
            {"name": "GitHub Sync", "description": "Sync repos", "category": "dev"}]
    r = search_v2(query="slack", apps=apps)
    assert r["total"] == 1
    assert r["results"][0]["name"] == "Slack Bot"

def test_filter():
    apps = [{"name": "A Tool", "category": "dev", "description": "tool"},
            {"name": "B Tool", "category": "comm", "description": "tool"}]
    r = search_v2(query="tool", apps=apps, filters={"category": "dev"})
    assert r["total"] == 1

def test_sort():
    apps = [{"name": "A App", "description": "app", "install_count": 10},
            {"name": "B App", "description": "app", "install_count": 100}]
    r = search_v2(query="app", apps=apps, sort_by="installs")
    assert r["results"][0]["install_count"] == 100

def test_pagination():
    apps = [{"name": f"App {i}", "description": "app"} for i in range(50)]
    r = search_v2(query="app", apps=apps, page=2, per_page=20)
    assert len(r["results"]) == 20
    assert r["total_pages"] == 3

from app.services.app_marketplace_app_app_app_app_app_app_app_search_index import build_index, search_index

def test_index():
    apps = [
        {"id": "app1", "name": "Slack Bot", "description": "chat integration", "category": "communication", "tags": ["slack"]},
        {"id": "app2", "name": "GitHub Sync", "description": "code sync", "category": "dev-tools", "tags": ["github"]},
    ]
    idx = build_index(apps)
    assert idx["app_count"] == 2
    assert idx["index_size"] > 0
    r = search_index(idx["index"], "slack")
    assert "app1" in r
    r2 = search_index(idx["index"], "sync")
    assert "app2" in r2

def test_multi_term():
    apps = [
        {"id": "a1", "name": "Slack Chat Bot", "tags": []},
        {"id": "a2", "name": "Slack Notifier", "tags": []},
    ]
    idx = build_index(apps)
    r = search_index(idx["index"], "slack bot")
    assert "a1" in r
    assert "a2" not in r  # "bot" not in notifier

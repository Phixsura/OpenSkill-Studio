from app.services.app_marketplace_app_app_app_app_app_app_app_platform_search import search_platform

def test_search():
    entities = [
        {"name": "API Gateway", "type": "service", "description": "Routes requests"},
        {"name": "DB Migration", "type": "runbook", "description": "Database migration guide"},
        {"name": "Auth Service", "type": "service", "description": "Authentication"},
    ]
    r = search_platform("api", entities)
    assert r["total_matches"] == 1
    assert r["results"][0]["name"] == "API Gateway"

def test_desc_match():
    entities = [{"name": "X", "type": "doc", "description": "API authentication guide"}]
    r = search_platform("authentication", entities)
    assert r["total_matches"] == 1

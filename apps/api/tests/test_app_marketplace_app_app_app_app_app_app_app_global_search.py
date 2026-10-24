from app.services.app_marketplace_app_app_app_app_app_app_app_global_search import search_all, suggest_completions

def test_search():
    entities = [
        {"name": "Auth Service", "type": "app", "description": "Authentication"},
        {"name": "User Profile", "type": "document", "description": "User settings"},
        {"name": "Analytics Dashboard", "type": "app", "description": "Data analytics"},
    ]
    r = search_all("auth", entities)
    assert r["total_matches"] == 1
    assert r["results"][0]["name"] == "Auth Service"

def test_suggest():
    names = ["Auth Service", "API Gateway", "Analytics", "Billing"]
    r = suggest_completions("a", names)
    assert "Auth Service" in r
    assert "Analytics" in r
    assert "Billing" not in r

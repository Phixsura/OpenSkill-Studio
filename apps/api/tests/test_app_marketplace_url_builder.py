from app.services.app_marketplace_url_builder import build_app_url, build_developer_url, build_search_url, build_api_url

def test_app_url():
    assert build_app_url(slug="super-app") == "https://openskill.dev/marketplace/apps/super-app"

def test_developer_url():
    assert "developers/devco" in build_developer_url(slug="devco")

def test_search():
    u = build_search_url(query="webhook", filters={"category": "connector"})
    assert "q=webhook" in u
    assert "category=connector" in u

def test_api():
    assert build_api_url(path="/users") == "https://openskill.dev/api/v1/users"
    assert build_api_url(path="/apps", version="v2") == "https://openskill.dev/api/v2/apps"

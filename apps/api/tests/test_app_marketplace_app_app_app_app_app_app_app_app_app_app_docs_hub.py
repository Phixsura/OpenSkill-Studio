from app.services.app_marketplace_app_app_app_app_app_app_app_app_app_app_docs_hub import build_docs_hub

def test_hub():
    r = build_docs_hub()
    assert r["total_sections"] == 10
    assert r["total_pages"] > 100

def test_search():
    r = build_docs_hub(search_query="security")
    assert r["total_sections"] == 1
    assert r["sections"][0]["id"] == "security"

from app.services.app_marketplace_complete_docs_page import build_complete_docs_page

def test_page():
    pages = [{"slug": "getting-started", "title": "Getting Started", "order": 0},
             {"slug": "api", "title": "API Reference", "order": 1}]
    p = build_complete_docs_page(app={"id": "a1", "name": "App"}, pages=pages,
                                   current_page=pages[0], api_version="v2")
    assert p["total_pages"] == 2
    assert p["sidebar"][0]["title"] == "Getting Started"
    assert p["current_page"]["slug"] == "getting-started"

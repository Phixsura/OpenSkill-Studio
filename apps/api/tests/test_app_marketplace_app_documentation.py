from app.services.app_marketplace_app_documentation import create_doc_page, build_doc_sidebar, search_docs

def test_create():
    p = create_doc_page(app_id="a1", slug="getting-started", title="Getting Started",
                         content="This guide helps you set up the app quickly.")
    assert p["slug"] == "getting-started"

def test_too_short():
    p = create_doc_page(app_id="a1", slug="x", title="Hi", content="Short")
    assert p["error"]

def test_sidebar():
    pages = [
        {"slug": "intro", "title": "Introduction", "order": 0, "parent_slug": None},
        {"slug": "api", "title": "API Reference", "order": 1, "parent_slug": None},
        {"slug": "auth", "title": "Authentication", "order": 0, "parent_slug": "api"},
    ]
    tree = build_doc_sidebar(pages=pages)
    assert tree[0]["slug"] == "intro"
    assert len(tree[1]["children"]) == 1

def test_search():
    pages = [
        {"slug": "auth", "title": "Authentication", "content": "OAuth and API keys"},
        {"slug": "intro", "title": "Introduction", "content": "Welcome to the app"},
    ]
    results = search_docs(pages=pages, query="auth")
    assert results[0]["slug"] == "auth"

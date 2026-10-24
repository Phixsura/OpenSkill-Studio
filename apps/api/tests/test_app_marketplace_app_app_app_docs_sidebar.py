from app.services.app_marketplace_app_app_app_docs_sidebar import build_docs_sidebar

def test_sidebar():
    sections = [
        {"title": "Getting Started", "icon": "🚀", "pages": [
            {"title": "Installation", "path": "/docs/install"},
            {"title": "Quick Start", "path": "/docs/quickstart"},
        ]},
        {"title": "API", "icon": "📋", "pages": [
            {"title": "Authentication", "path": "/docs/api/auth"},
        ]},
    ]
    r = build_docs_sidebar(sections=sections, active_path="/docs/install")
    assert r["section_count"] == 2
    assert r["total_pages"] == 3
    assert r["sections"][0]["expanded"]  # has active page
    assert not r["sections"][1]["expanded"]

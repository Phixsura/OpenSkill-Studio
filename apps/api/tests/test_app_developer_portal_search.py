from app.services.app_developer_portal_search import portal_search

APPS = [{"id": "a1", "name": "LMS Connector", "slug": "lms-conn"}]
DOCS = [{"title": "Quick Start Guide", "url": "/docs/quickstart"}]

def test_search_app():
    r = portal_search("lms", apps=APPS)
    assert r["total"] == 1
    assert r["results"][0]["type"] == "app"

def test_search_doc():
    r = portal_search("quick start", docs=DOCS)
    assert r["total"] == 1

def test_empty_query():
    r = portal_search("")
    assert r["total"] == 0

def test_no_match():
    r = portal_search("nonexistent", apps=APPS, docs=DOCS)
    assert r["total"] == 0

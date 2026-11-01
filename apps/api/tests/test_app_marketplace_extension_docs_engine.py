from app.services.app_marketplace_extension_docs_engine import ExtDocsEngineService

def test_add_and_get():
    svc = ExtDocsEngineService()
    svc.add_page("ext-1", "getting-started", "Getting Started", "# Welcome\nStart here.", "guide", 0)
    page = svc.get_page("ext-1", "getting-started")
    assert page is not None
    assert page.title == "Getting Started"

def test_toc():
    svc = ExtDocsEngineService()
    svc.add_page("ext-1", "intro", "Intro", "content", "guide", 0)
    svc.add_page("ext-1", "api", "API Ref", "content", "api", 1)
    toc = svc.get_toc("ext-1")
    assert len(toc) == 2

def test_search():
    svc = ExtDocsEngineService()
    svc.add_page("ext-1", "auth", "Authentication", "OAuth2 flow guide")
    svc.add_page("ext-1", "data", "Data API", "CRUD operations")
    results = svc.search("ext-1", "oauth")
    assert len(results) == 1

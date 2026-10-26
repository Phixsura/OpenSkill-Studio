from app.services.app_marketplace_extension_docs_hub import ExtensionDocsHubService

def test_add_and_get():
    svc = ExtensionDocsHubService()
    svc.add_page("quickstart", "Quick Start", "getting-started", "# Quick Start\nGet going fast")
    page = svc.get_page("quickstart")
    assert page.title == "Quick Start"

def test_search():
    svc = ExtensionDocsHubService()
    svc.add_page("auth", "Authentication", "security", "How to authenticate")
    svc.add_page("deploy", "Deployment", "ops", "How to deploy")
    results = svc.search("authenticate")
    assert len(results) == 1

def test_categories():
    svc = ExtensionDocsHubService()
    svc.add_page("a", "A", "guide", "content", order=2)
    svc.add_page("b", "B", "guide", "content", order=1)
    svc.add_page("c", "C", "api", "content")
    cats = svc.get_categories()
    assert len(cats) == 2
    assert cats["guide"][0].slug == "b"  # ordered

def test_reading_progress():
    svc = ExtensionDocsHubService()
    svc.add_page("a", "A", "g", "c")
    svc.add_page("b", "B", "g", "c")
    svc.mark_read("user-1", "a")
    progress = svc.get_reading_progress("user-1")
    assert progress["percent"] == 50

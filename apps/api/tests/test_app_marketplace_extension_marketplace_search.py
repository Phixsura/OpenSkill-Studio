from app.services.app_marketplace_extension_marketplace_search import MarketplaceSearchService, SearchableExt

def test_search():
    svc = MarketplaceSearchService()
    svc.index(SearchableExt("e1", "Auth Plugin", "Authentication helper", ["auth"], installs=100))
    svc.index(SearchableExt("e2", "Data Grid", "Grid component", ["ui"], installs=200))
    results = svc.search("auth")
    assert len(results) == 1
    assert results[0].extension_id == "e1"

def test_sort_by_installs():
    svc = MarketplaceSearchService()
    svc.index(SearchableExt("e1", "Plugin A", "A plugin", installs=50))
    svc.index(SearchableExt("e2", "Plugin B", "B plugin", installs=500))
    results = svc.search("plugin", sort_by="installs")
    assert results[0].extension_id == "e2"

def test_suggest():
    svc = MarketplaceSearchService()
    svc.index(SearchableExt("e1", "Auth Plugin", "desc"))
    svc.index(SearchableExt("e2", "Auth Manager", "desc"))
    svc.index(SearchableExt("e3", "Data Grid", "desc"))
    suggestions = svc.suggest("auth")
    assert len(suggestions) == 2

def test_filter_by_tag():
    svc = MarketplaceSearchService()
    svc.index(SearchableExt("e1", "Widget A", "A widget", ["ui"]))
    svc.index(SearchableExt("e2", "Widget B", "B widget", ["api"]))
    results = svc.search("widget", tag="ui")
    assert len(results) == 1

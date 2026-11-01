from app.services.app_marketplace_search_autocomplete import SearchAutocomplete, build_suggestions_response

def test_prefix_match():
    ac = SearchAutocomplete()
    ac.index([{"name": "GitHub Connector", "slug": "gh"}, {"name": "GitLab Sync", "slug": "gl"},
              {"name": "Slack Bot", "slug": "sl"}])
    results = ac.suggest("git")
    assert len(results) == 2

def test_substring_match():
    ac = SearchAutocomplete()
    ac.index([{"name": "My Connector", "slug": "mc"}])
    results = ac.suggest("conn")
    assert len(results) == 1

def test_tag_match():
    ac = SearchAutocomplete()
    ac.index([{"name": "App", "tags": ["automation", "workflow"]}])
    results = ac.suggest("auto")
    assert len(results) == 1

def test_min_length():
    ac = SearchAutocomplete()
    ac.index([{"name": "X"}])
    assert ac.suggest("x") == []

def test_response():
    r = build_suggestions_response(suggestions=[{"name": "App", "slug": "app", "category": "connector"}])
    assert r["count"] == 1
    assert r["suggestions"][0]["type"] == "app"

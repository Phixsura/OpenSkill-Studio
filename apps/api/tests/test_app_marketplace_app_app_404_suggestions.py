from app.services.app_marketplace_app_app_404_suggestions import suggest_pages

PAGES = ["/docs/getting-started", "/docs/api-reference", "/docs/webhooks",
         "/apps/marketplace", "/apps/my-apps", "/settings/account"]

def test_similar():
    r = suggest_pages(requested_path="/docs/getting-starte", available_paths=PAGES)
    assert r["has_suggestions"]
    assert "/docs/getting-started" in r["suggestions"]

def test_category():
    r = suggest_pages(requested_path="/docs/nonexistent", available_paths=PAGES)
    assert len(r["category_matches"]) > 0

def test_no_match():
    r = suggest_pages(requested_path="/zzzzzzz", available_paths=PAGES)
    # May or may not have suggestions depending on cutoff
    assert isinstance(r["suggestions"], list)

from app.services.app_marketplace_sitemap import generate_sitemap_entries, render_sitemap_xml

def test_entries():
    entries = generate_sitemap_entries(
        apps=[{"slug": "app-a", "status": "published"}, {"slug": "draft", "status": "draft"}],
        developers=[{"slug": "dev1"}], collections=[{"slug": "best"}])
    slugs = [e["loc"] for e in entries]
    assert any("app-a" in s for s in slugs)
    assert not any("draft" in s for s in slugs)
    assert any("dev1" in s for s in slugs)
    assert len(entries) == 4  # home + 1 app + 1 dev + 1 col

def test_xml():
    xml = render_sitemap_xml(entries=[{"loc": "https://x.com/a", "priority": "1.0"}])
    assert "<?xml" in xml
    assert "<loc>https://x.com/a</loc>" in xml

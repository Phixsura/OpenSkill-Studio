from app.services.app_marketplace_sitemap_final import build_complete_sitemap

def test_sitemap():
    s = build_complete_sitemap(
        apps=[{"slug": "app1", "status": "published"}, {"slug": "app2", "status": "draft"}],
        developers=[{"slug": "dev1"}], collections=[{"slug": "best"}],
        categories=[{"id": "connector"}], blog_posts=[{"slug": "post1"}])
    assert s["static_count"] >= 17
    assert s["dynamic_count"] == 5  # 1 published app + 1 dev + 1 collection + 1 category + 1 blog... wait
    # Actually: 1 app (draft excluded) + 1 dev + 1 col + 1 cat + 1 blog = 5
    assert s["dynamic_count"] == 5
    assert s["total"] == s["static_count"] + s["dynamic_count"]

def test_empty():
    s = build_complete_sitemap(apps=[], developers=[], collections=[], categories=[], blog_posts=[])
    assert s["dynamic_count"] == 0
    assert s["static_count"] >= 17

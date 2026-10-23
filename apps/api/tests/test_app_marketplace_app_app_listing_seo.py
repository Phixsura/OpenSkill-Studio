from app.services.app_marketplace_app_app_listing_seo import analyze_seo, generate_meta_tags

def test_good_seo():
    r = analyze_seo(title="My Awesome App for Teams",
        description="A " * 60, category="productivity", tags=["tool", "team", "project"])
    assert r["grade"] in ("A", "B")
    assert r["issue_count"] == 0

def test_poor_seo():
    r = analyze_seo(title="App", description="Short", category="", tags=[])
    assert r["grade"] in ("C", "F")
    assert r["issue_count"] >= 3

def test_meta():
    r = generate_meta_tags(title="My App", description="A great app for teams",
        image_url="https://example.com/img.png", url="https://marketplace.dev/apps/1")
    assert r["tags"]["og:title"] == "My App"
    assert "og:image" in r["tags"]

def test_meta_xss():
    r = generate_meta_tags(title='<script>alert("xss")</script>', description="ok")
    assert "<script>" not in r["tags"]["title"]

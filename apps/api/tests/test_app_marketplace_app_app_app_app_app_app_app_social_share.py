from app.services.app_marketplace_app_app_app_app_app_app_app_social_share import build_share_links, build_og_meta

def test_share():
    r = build_share_links(title="My App", url="https://openskill.io/apps/myapp")
    assert "twitter.com" in r["twitter"]
    assert "linkedin.com" in r["linkedin"]
    assert r["copy_url"] == "https://openskill.io/apps/myapp"

def test_og():
    r = build_og_meta(title="My App", description="A great app", image="https://img/og.png")
    assert r["og:title"] == "My App"
    assert r["twitter:card"] == "summary_large_image"

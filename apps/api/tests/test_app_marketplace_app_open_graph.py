from app.services.app_marketplace_app_open_graph import generate_og_tags

def test_generate():
    r = generate_og_tags(app_name="Auth SDK", description="Best authentication solution",
        url="https://marketplace.openskill.dev/apps/auth-sdk",
        image_url="https://cdn.openskill.dev/auth-sdk.png")
    assert r["tags"]["og:title"] == "Auth SDK"
    assert "og:image" in r["tags"]
    assert "twitter:card" in r["tags"]
    assert '<meta property="og:title"' in r["meta_html"]

def test_xss():
    r = generate_og_tags(app_name='<script>alert("xss")</script>', description="ok",
        url="https://example.com")
    assert "<script>" not in r["tags"]["og:title"]
    assert "<script>" not in r["meta_html"]

def test_no_image():
    r = generate_og_tags(app_name="App", description="Desc", url="https://x.com")
    assert "og:image" not in r["tags"]

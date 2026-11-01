from app.services.app_marketplace_app_app_link_preview import generate_link_preview

def test_preview():
    r = generate_link_preview(url="https://marketplace.openskill.dev/apps/auth",
        title="Auth SDK", description="Best auth solution for developers",
        image_url="https://cdn.openskill.dev/auth.png")
    assert r["title"] == "Auth SDK"
    assert r["domain"] == "marketplace.openskill.dev"
    assert r["has_image"]

def test_no_image():
    r = generate_link_preview(url="https://example.com", title="X", description="Y")
    assert not r["has_image"]

def test_xss():
    r = generate_link_preview(url="x", title="<script>xss</script>", description="ok")
    assert "<script>" not in r["title"]

from app.services.app_marketplace_app_app_og_meta import build_og_meta

def test_basic():
    r = build_og_meta(title="SuperApp", description="A great app", url="https://marketplace.openskill.dev/apps/superapp")
    assert r["tag_count"] >= 8
    assert any(t["property"] == "og:title" and t["content"] == "SuperApp" for t in r["tags"] if "property" in t)
    assert "og:title" in r["html"]

def test_with_image():
    r = build_og_meta(title="X", description="Y", url="https://x.com", image="https://img.com/og.png")
    assert any(t.get("property") == "og:image" for t in r["tags"])

def test_bad_url():
    r = build_og_meta(title="X", description="Y", url="javascript:alert(1)")
    assert "error" in r

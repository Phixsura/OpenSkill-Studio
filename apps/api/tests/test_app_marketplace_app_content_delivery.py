from app.services.app_marketplace_app_content_delivery import generate_asset_url, compute_content_hash, build_asset_manifest, invalidate_cache

def test_url():
    u = generate_asset_url(app_slug="my-app", version="2.0", path="main.js")
    assert u == "https://cdn.openskill.dev/apps/my-app/2.0/main.js"

def test_hash():
    h = compute_content_hash(content=b"hello world")
    assert len(h) == 16

def test_manifest():
    m = build_asset_manifest(assets=[{"path": "app.js", "hash": "abc", "size": 1024, "content_type": "application/javascript"}], version="1.0")
    assert m["version"] == "1.0"
    assert m["total_size"] == 1024

def test_invalidate():
    r = invalidate_cache(paths=["/app.js", "/style.css"], app_slug="my-app")
    assert r["count"] == 2

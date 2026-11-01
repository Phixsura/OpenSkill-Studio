from app.services.app_marketplace_content_delivery import ContentDeliveryService


def test_upload_and_get():
    cdn = ContentDeliveryService()
    asset = cdn.upload_asset("ext-1", "1.0.0", "dist/bundle.js", b"console.log('hi')", "application/javascript")
    assert asset.size_bytes == 17
    assert "cdn.openskill.dev" in asset.cdn_url
    assert len(asset.content_hash) == 64
    fetched = cdn.get_asset("ext-1", "1.0.0", "dist/bundle.js")
    assert fetched is not None


def test_cdn_url():
    cdn = ContentDeliveryService()
    cdn.upload_asset("ext-2", "2.0.0", "icon.png", b"PNG_DATA", "image/png")
    url = cdn.get_cdn_url("ext-2", "2.0.0", "icon.png")
    assert url is not None
    assert "ext-2" in url
    assert "2.0.0" in url


def test_list_assets():
    cdn = ContentDeliveryService()
    cdn.upload_asset("ext-3", "1.0.0", "a.js", b"a", "application/javascript")
    cdn.upload_asset("ext-3", "1.0.0", "b.css", b"b", "text/css")
    cdn.upload_asset("ext-3", "2.0.0", "a.js", b"a2", "application/javascript")
    v1 = cdn.list_assets("ext-3", "1.0.0")
    assert len(v1) == 2
    all_assets = cdn.list_assets("ext-3")
    assert len(all_assets) == 3


def test_invalidate_cache():
    cdn = ContentDeliveryService()
    cdn.upload_asset("ext-4", "1.0.0", "main.js", b"code")
    result = cdn.invalidate_cache("ext-4", "1.0.0", ["main.js"])
    assert result["paths"] == ["main.js"]


def test_total_size():
    cdn = ContentDeliveryService()
    cdn.upload_asset("ext-5", "1.0.0", "a.js", b"x" * 100)
    cdn.upload_asset("ext-5", "1.0.0", "b.js", b"y" * 200)
    assert cdn.get_total_size("ext-5", "1.0.0") == 300


def test_delete_version():
    cdn = ContentDeliveryService()
    cdn.upload_asset("ext-6", "1.0.0", "a.js", b"a")
    cdn.upload_asset("ext-6", "1.0.0", "b.js", b"b")
    cdn.upload_asset("ext-6", "2.0.0", "a.js", b"a2")
    deleted = cdn.delete_version_assets("ext-6", "1.0.0")
    assert deleted == 2
    assert len(cdn.list_assets("ext-6")) == 1

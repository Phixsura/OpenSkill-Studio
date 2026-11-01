from app.services.app_marketplace_extension_content_delivery import ExtContentDeliveryService

def test_publish_and_get():
    svc = ExtContentDeliveryService()
    asset = svc.publish("ext-1", "/ext/1/main.js", b"console.log('hi')")
    assert asset.size_bytes == 17
    retrieved = svc.get("/ext/1/main.js")
    assert retrieved is not None
    assert retrieved.content_hash == asset.content_hash

def test_invalidate():
    svc = ExtContentDeliveryService()
    svc.publish("ext-1", "/ext/1/app.js", b"code")
    assert svc.invalidate("/ext/1/app.js") is True
    assert svc.get("/ext/1/app.js") is None

def test_invalidate_extension():
    svc = ExtContentDeliveryService()
    svc.publish("ext-1", "/a.js", b"a")
    svc.publish("ext-1", "/b.js", b"b")
    svc.publish("ext-2", "/c.js", b"c")
    assert svc.invalidate_extension("ext-1") == 2
    assert svc.get("/c.js") is not None

def test_stats():
    svc = ExtContentDeliveryService()
    svc.publish("ext-1", "/x.js", b"x" * 100)
    stats = svc.get_stats()
    assert stats["total_assets"] == 1
    assert stats["total_size_bytes"] == 100

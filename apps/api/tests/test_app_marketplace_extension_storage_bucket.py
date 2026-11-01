from app.services.app_marketplace_extension_storage_bucket import ExtStorageBucketService

def test_put_and_get():
    svc = ExtStorageBucketService()
    obj = svc.put("ext-1", "assets/logo.png", b"PNG_DATA", "image/png")
    assert obj.size_bytes == 8
    retrieved = svc.get("ext-1", "assets/logo.png")
    assert retrieved is not None

def test_path_traversal():
    svc = ExtStorageBucketService()
    try:
        svc.put("ext-1", "../etc/passwd", b"hack")
        assert False
    except ValueError:
        pass

def test_list_with_prefix():
    svc = ExtStorageBucketService()
    svc.put("ext-1", "images/a.png", b"a")
    svc.put("ext-1", "images/b.png", b"b")
    svc.put("ext-1", "docs/readme.md", b"r")
    assert len(svc.list_objects("ext-1", "images/")) == 2

def test_delete_and_usage():
    svc = ExtStorageBucketService()
    svc.put("ext-1", "file.txt", b"hello")
    assert svc.get_usage("ext-1")["object_count"] == 1
    svc.delete("ext-1", "file.txt")
    assert svc.get_usage("ext-1")["object_count"] == 0

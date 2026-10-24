from app.services.app_marketplace_app_container_registry import push_image, list_images, delete_image

def test_push():
    r = push_image(repository="myapp/api", tag="v2.0.0", size_mb=145.2)
    assert r["status"] == "pushed"
    assert r["full_ref"] == "registry.openskill.dev/myapp/api:v2.0.0"
    assert r["digest"].startswith("sha256:")

def test_invalid_tag():
    r = push_image(repository="x", tag="bad tag!", size_mb=10)
    assert "error" in r

def test_list():
    r = list_images(repository="myapp/api")
    assert r["total"] == 3
    assert r["total_size_mb"] == 426.5

def test_delete():
    r = delete_image(repository="myapp/api", tag="v1.9.0")
    assert r["deleted"]

def test_delete_latest():
    r = delete_image(repository="myapp/api", tag="latest")
    assert "error" in r
